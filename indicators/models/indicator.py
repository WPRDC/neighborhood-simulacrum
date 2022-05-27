import dataclasses
import logging
from typing import Optional, TYPE_CHECKING, List, TypedDict

from colorama import Fore, Style
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.text import slugify
from markdownx.models import MarkdownxField

from context.models import WithContext, WithTags
from geo.models import AdminRegion
from indicators.data import Datum, GeogCollection, GeogRecord
from indicators.errors import AggregationError, DataRetrievalError
from indicators.utils import ErrorRecord, DataResponse, ErrorLevel
from maps.util import menu_view_name
from profiles.abstract_models import Described
from indicators.models.source import Source
from maps.models import DataLayer

if TYPE_CHECKING:
    from indicators.models.variable import Variable
    from indicators.models.time import TimeAxis

logger = logging.getLogger(__name__)


class IndicatorVariable(models.Model):
    """ Links Indicator to Variable  """
    indicator = models.ForeignKey(
        'Indicator',
        on_delete=models.CASCADE,
        related_name='indicator_to_variable'
    )
    variable = models.ForeignKey(
        'Variable',
        on_delete=models.CASCADE,
        related_name='variable_to_indicator'
    )
    order = models.IntegerField()

    def get_data_layer(self, geog_collection: 'GeogCollection'):
        return DataLayer.get_or_create_updated_map(
            geog_collection,
            self.indicator.time_axis,
            self.variable,
            self.indicator.use_denominators
        )

    class Meta:
        ordering = ['order']


class Indicator(WithTags, WithContext, Described):
    """ Base class for all Data Presentations """

    @dataclasses.dataclass()
    class Dimensions:
        class ResponseDict(TypedDict):
            geog: list[str]
            time: list[str]
            vars: list[str]

        geog: QuerySet['AdminRegion'] = dataclasses.field(default_factory=list)
        time: list['TimeAxis.TimePart'] = dataclasses.field(default_factory=list)
        vars: QuerySet['Variable'] = dataclasses.field(default_factory=list)

        @property
        def response_dict(self) -> ResponseDict:
            return {
                'geog': [x.slug for x in self.geog],
                'time': [x.slug for x in self.time],
                'vars': [x.slug for x in self.vars],
            }

    # Axes
    time_axis = models.ForeignKey(
        'TimeAxis',
        related_name='indicators',
        on_delete=models.CASCADE
    )
    vars = models.ManyToManyField(
        'Variable',
        verbose_name='Variables',
        through='IndicatorVariable'
    )
    across_geogs = models.BooleanField(
        verbose_name='Allow cross-geog vizes',
        help_text='Leave true in nearly all cases.',
        default=True)

    # Indicator with same time axis
    mirror_indicator = models.OneToOneField(
        'Indicator',
        help_text='e.g. pop-by-age-male if this indicator is pop-my-age-female would allow a pyramid chart',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Metadata
    note = MarkdownxField(
        verbose_name='Brief note',
        blank=True,
        null=True
    )

    # Viz Overrides
    use_columns = models.BooleanField(
        verbose_name='Prefer column layout in bar charts (if any)',
        help_text='constraints may require apps and sites to override to bar chart when space is limited.',
        default=False
    )
    use_denominators = models.BooleanField(
        verbose_name='Use denominators and percents in visualizations',
        help_text='(Usually left true)',
        default=True
    )

    dimension_order = ['geog', 'time', 'var']

    _neighbor_geogs = None

    @property
    def variables(self) -> QuerySet['Variable']:
        """ Public property for accessing the variables in the indicator. """
        return self.vars.order_by('variable_to_indicator')

    @property
    def options(self) -> dict:
        return {
            'note': self.note,
            'use_columns': self.use_columns,
            'use_denominators': self.use_denominators,
        }

    @property
    def sources(self) -> QuerySet['Source']:
        """ Queryset representing the set of sources attached to all variables in this indicator. """
        source_ids = set()
        variable: Variable
        for variable in self.variables:
            var_source_ids = [s.id for s in variable.sources.all()]
            for var_source_id in var_source_ids:
                source_ids.add(var_source_id)
        return Source.objects.filter(pk__in=list(source_ids))

    @property
    def children(self) -> List[QuerySet]:
        from indicators.models import TimeAxis
        return [self.sources, self.variables, TimeAxis.objects.filter(id=self.time_axis.id)]

    @property
    def multidimensional(self):
        return {
            'geog': self.across_geogs,
            'time': len(self.time_axis.time_parts) > 1,
            'vars': len(self.variables) > 1,
        }

    @property
    def is_mappable(self):
        """ Currently only mapping cross-geog with one time and one var """
        return (
                self.multidimensional['geog']
                and not self.multidimensional['time']
                and not self.multidimensional['vars']
        )

    def can_handle_geography(self, geog: 'AdminRegion') -> bool:
        """
        Returns `True` if the variables in this visualization and, in turn, their sources, work
        with the supplied geography.
        :param geog:
        :return:
        """
        var: 'Variable'
        for var in self.vars.all():
            if not var.can_handle_geography(geog):
                return False
        return True

    def can_handle_geographies(self, geogs: QuerySet['AdminRegion']) -> bool:
        for geog in geogs.all():
            if not self.can_handle_geography(geog):
                return False
        return True

    def get_subgeogs(self, geog: 'AdminRegion') -> QuerySet['AdminRegion']:
        """
        Returns a queryset representing the minimum set of geographies to for which data can be
        aggregated to represent `geog` and a bool representing whether child geogs are used.

        `None` is returned if no such non-empty set exists.

        :param geog: the geography being examined
        :raises AggregationError: if aggregation isn't possible
        :return: Queryset of geographies to for which data can be aggregated to represent `geog`; None if an emtpy set.
        """
        # does it work directly for the goeg?
        if self.can_handle_geography(geog):
            return type(geog).objects.filter(global_geoid=geog.global_geoid)

        # does it work as an aggregate over a smaller geog?
        for subgeog_type_id in AdminRegion.SUBGEOG_TYPE_ORDER:
            if subgeog_type_id in geog.subregions:
                subgeog_model = AdminRegion.find_subclass(subgeog_type_id)
                subgeog_global_geoids = geog.subregions[subgeog_type_id]
                sub_geogs: QuerySet['AdminRegion'] = subgeog_model.objects.filter(
                    global_geoid__in=subgeog_global_geoids)

                if self.can_handle_geographies(sub_geogs):
                    return sub_geogs

        # if it required aggregation but no suitable subgeogs were found
        raise AggregationError(f'{self.title} not available for {geog.title}.')

    def get_neighbor_geogs(self, geog: 'AdminRegion') -> QuerySet['AdminRegion']:
        """ Generates queryset of all neighbor geographies to be compared with `geog` also includes geog. """
        if self._neighbor_geogs is None:
            if self.across_geogs:
                self._neighbor_geogs = geog.__class__.objects.filter(in_extent=True)
            self._neighbor_geogs = geog.__class__.objects.filter(global_geoid=geog.global_geoid)
        return self._neighbor_geogs

    def get_data(self, geog: 'AdminRegion') -> DataResponse:
        """
        Returns a `DataResponse` object with the viz's data at `geog`.

        This method is the primary interface to request data.
        Generalized solution
            1. Get full set of geogs necessary for viz
              a. get set of neighbor geogs, including the primary geog, if necessary for the viz
                  (e.g. a map of neighborhoods, table across counties)
              b. for each geog in the set, find the set of subgeogs necessary for the source.
                  if not necessary, the subgeog set will just be [geog]
            2. For each variable in the data viz,
              a. get values for full set of subgeogs
              b. aggregate those values up to the set of neighbor geogs
            3. Use data on set of neighbor geogs to populate response

        :param geog: the geography being examined
        :return: DataResponse with data and error information
        """
        data: Optional[list[list[list[dict]]]] = None
        dimensions: Indicator.Dimensions = Indicator.Dimensions()
        map_options: Optional[dict] = None
        error = ErrorRecord(level=ErrorLevel.OK, message='')
        warnings: Optional[list[ErrorRecord]] = None

        try:
            # 1. Get full set of geogs necessary for viz
            #   a. get set of neighbor geogs including the primary geog if necessary for teh viz
            neighbor_geogs = self.get_neighbor_geogs(geog)

            #   b. for each geog in the set, find the set of subgeogs that work for the source.
            #         if no subgeogs are necessary, the subgeog set will just be [geog]
            geog_collection = GeogCollection(geog_type=type(geog), primary_geog=geog)
            for neighbor_geog in neighbor_geogs:
                geog_collection.records[neighbor_geog.global_geoid] = GeogRecord(
                    geog=neighbor_geog,
                    subgeogs=self.get_subgeogs(neighbor_geog),
                )

            # 2. For each variable in the data viz,
            #   a. get values for full set of subgeogs
            #   b. aggregate those values up to the set of neighbor geogs
            # this is done in the private method which may be overridden to
            # handle difference cases for difference visualizations

            # todo: add information about geographic aggregation if it occureda
            #   - list of subgeogs so we can link to them on Apps and sites
            if neighbor_geogs:
                dimensions = self._get_dimensions(neighbor_geogs)
                data, warnings = self._get_data(geog_collection, dimensions)
                if self.is_mappable:
                    map_options = self._get_map_options(geog_collection)
            else:
                error = ErrorRecord(level=ErrorLevel.EMPTY,
                                    message=f'This visualization is not available for {geog.name}.')
            return DataResponse(data, dimensions, map_options, error, warnings=warnings)

        except DataRetrievalError as e:
            logger.error(str(e))
            error = e.error_response
            return DataResponse(data, dimensions, map_options, error, warnings=warnings)

        except Exception as e:
            logger.exception(str(e))
            print(f'{Fore.RED}Uncaught Error:', e, Style.RESET_ALL)
            raise e

    def _get_data(
            self,
            geog_collection: GeogCollection,
            dimensions: 'Indicator.Dimensions'
    ) -> (list[list[list[dict]]], list[ErrorRecord]):
        """
        Gets a representation of data for the viz.

        All the nitty-gritty work of spatial, temporal and categorical harmonization happens here. Any inability to
        harmonize should return an empty dataset and an error response explaining what went wrong (e.g. not available
        for 'geog' because of privacy reasons)

        Override when necessary.

        If representing the data as a list of records doesn't make sense for the visualization (e.g. maps),
        this method can be overridden.
        """
        data: dict[str, Datum] = {}
        warnings: list[ErrorRecord] = []
        message_dupes = set()

        for variable in self.variables:
            var_data, var_warnings = variable.get_values(geog_collection, self.time_axis)
            for item in var_data:
                data[f'{item.geog}:{item.time}:{item.variable}'] = item
            for warning in var_warnings:
                if warning.message not in message_dupes:
                    message_dupes.add(warning.message)
                    warnings.append(warning)

        # place results in a 3d array following the order in `dimensions`
        results: list[list[list[dict]]] = []
        for geog in dimensions.geog:
            g_list: list[list[dict]] = []
            for time_part in dimensions.time:
                t_list: list[dict] = []
                for var in dimensions.vars:
                    t_list.append(data[f'{geog.global_geoid}:{time_part.slug}:{var.slug}'].data)
                g_list.append(t_list)
            results.append(g_list)

        return results, warnings

    def _get_map_options(self, geog_collection: GeogCollection) -> Optional[dict]:
        """
        Collects and returns the data for this indicator at the `geog` provided
        """
        sources: [dict] = []
        layers: [dict] = []
        interactive_layer_ids: [str] = []
        legend_options: [dict] = []

        border_base_style = settings.MAP_STYLES

        for var in self.vars.all():
            layer: 'IndicatorVariable' = self.vars.through.objects.get(variable=var, indicator=self)
            data_layer: DataLayer = layer.get_data_layer(geog_collection)
            source, tmp_layers, interactive_layer_ids, legend_option = data_layer.get_map_options()
            sources.append(source)
            legend_options.append(legend_option)
            layers += tmp_layers

        primary_geog = geog_collection.primary_geog

        map_options: dict = {
            'interactive_layer_ids': interactive_layer_ids,
            'default_viewport': {
                'longitude': primary_geog.geom.centroid.x,
                'latitude': primary_geog.geom.centroid.y,
                'zoom': primary_geog.base_zoom - 1
            }
        }

        # for highlighting current geog
        highlight_id = slugify(primary_geog.name)
        highlight_source = {
            'id': f'{highlight_id}',
            'type': 'vector',
            'url': f"{settings.MAP_HOST}{menu_view_name(geog_collection.geog_type)}.json",
        }
        highlight_layer = {
            'id': f'{highlight_id}/highlight',
            'source': f'{highlight_id}',
            'source-layer': f'{highlight_id}',
            **border_base_style
        }
        sources.append(highlight_source)
        layers.append(highlight_layer)

        return {
            'sources': sources,
            'layers': layers,
            'legends': legend_options,
            'map_options': map_options
        }

    def _get_dimensions(self, neighbor_geogs: QuerySet['AdminRegion']) -> Dimensions:
        """ Returns dimensions for the data """
        return Indicator.Dimensions(
            geog=neighbor_geogs,
            time=self.time_axis.time_parts,
            vars=self.variables,
        )

    def __str__(self):
        return f'{self.name} ({self.__class__.__name__})'

    class Meta:
        verbose_name = "Data Visualization"
        verbose_name_plural = "Data Visualizations"


@receiver(m2m_changed, sender=Indicator.variables, dispatch_uid="check_var_timing")
def check_var_timing(_, instance: Indicator, **kwargs):
    for var in instance.vars.all():
        var: 'Variable'
        for time_part in instance.time_axis.time_parts:
            if not var.can_handle_time_part(time_part):
                raise ValidationError(f'{var.slug} is not available in time {time_part.slug}')
