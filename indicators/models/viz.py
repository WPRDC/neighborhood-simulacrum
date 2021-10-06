import logging
import re
from typing import TYPE_CHECKING, Type, Optional, Union

import pystache
from colorama import Fore, Style
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet, Manager
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.text import slugify
from polymorphic.models import PolymorphicModel

from indicators.errors import DataRetrievalError, EmptyResultsError
from indicators.models.source import Source
from indicators.utils import DataResponse, ErrorResponse, ErrorLevel
from maps.models import DataLayer
from profiles.abstract_models import Described

if TYPE_CHECKING:
    from indicators.models.variable import Variable
    from geo.models import AdminRegion

CARTO_REQUIRED_FIELDS = "cartodb_id, the_geom, the_geom_webmercator"

logger = logging.getLogger(__name__)

pattern = re.compile(r'(?<!^)(?=[A-Z])')


class VizVariable(models.Model):
    """ Common fields and methods for all variables attached to data vizes """
    order = models.IntegerField()

    class Meta:
        abstract = True
        ordering = ['order']


class DataViz(PolymorphicModel, Described):
    """ Base class for all Data Presentations """
    vars: Manager['Variable']
    time_axis = models.ForeignKey('TimeAxis', related_name='data_vizes', on_delete=models.CASCADE)
    indicator = models.ForeignKey('Indicator', related_name='old_data_vizes', on_delete=models.CASCADE)

    @property
    def variables(self) -> QuerySet['Variable']:
        """ Public property for accessing the variables int he viz. """
        variable_to_viz = f'variable_to_{self.ref_name}'
        if self.vars:
            return self.vars.order_by(variable_to_viz)
        raise AttributeError('Subclasses of DataPresentation must provide their own `vars` ManyToManyField')

    @property
    def options(self) -> dict:
        return {}

    @property
    def viz_type(self) -> str:
        return self.__class__.__qualname__

    @property
    def ref_name(self) -> str:
        """ The snake case string used to reference this model in related names. """
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.viz_type)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    @property
    def sources(self) -> QuerySet['Source']:
        """ Queryset representing the set of sources attached to all variables in this viz. """
        source_ids = set()
        variable: Variable
        for variable in self.variables:
            var_source_ids = [s.id for s in variable.sources.all()]
            for var_source_id in var_source_ids:
                source_ids.add(var_source_id)
        return Source.objects.filter(pk__in=list(source_ids))

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

    def get_geog_queryset(self, geog: 'AdminRegion') -> tuple[Optional[QuerySet['AdminRegion']], bool]:
        """
        Returns a queryset representing the the minimum set of geographies to for which data can be
        aggregated to represent `geog` and a bool representing whether or not child geogs are used.

        `None` is returned if no such non-empty set exists.

        :param geog: teh geography being examined
        :return: Queryset of geographies to for which data can be aggregated to represent `geog`; None if an emtpy set.
        """
        # check how geog works for this viz
        # does it work directly for the goeg?
        if self.can_handle_geography(geog):
            return type(geog).objects.filter(pk=geog.pk), False

        # does it work as an aggregate over a smaller geog?
        for child_geog_model in geog.child_geog_models:
            child_geogs = child_geog_model.objects.filter(mini_geom__coveredby=geog.big_geom)

            if self.can_handle_geographies(child_geogs):
                return child_geogs, True

        return None, False

    def get_viz_data(self, geog: 'AdminRegion') -> DataResponse:
        """
        Returns a `DataResponse` object with the viz's data at `geog`.

        This method is the primary interface to request data. Calls `_get_viz_data` which can be implemented
        in subclassed models.

        :param geog: the geography being examined
        :return: DataResponse with data and error information
        """
        # get queryset representing geog though itself or child geogs
        geogs, use_agg = self.get_geog_queryset(geog)
        # parent geog is just a geog unlesse we're doing maps or cross-geog charts, then we need to use the class
        parent_geog_lvl = geog if use_agg else None
        data, options, error = None, None, ErrorResponse(ErrorLevel.OK)
        try:
            if geogs:
                data = self._get_viz_data(geogs, parent_geog_lvl=parent_geog_lvl)
                options = self._get_viz_options(geog)
            else:
                error = ErrorResponse(level=ErrorLevel.EMPTY,
                                      message=f'This visualization is not available for {geog.name}.')
            return DataResponse(data, options, error)

        except DataRetrievalError as e:
            logger.error(str(e))
            error = e.error_response
            return DataResponse(data, options, error)

        except Exception as e:
            logger.exception(str(e))
            print(f'{Fore.RED}Uncaught Error:', e, Style.RESET_ALL)
            error = ErrorResponse(ErrorLevel.ERROR, f'Uncaught Error: {e}')
            raise e
            # return DataResponse(data, options, error)

    def _get_viz_data(self, geogs: QuerySet['AdminRegion'],
                      parent_geog_lvl: Optional[Union[Type['AdminRegion'], 'AdminRegion']] = None
                      ) -> list[dict]:
        """
        All the nitty-gritty work of spatial, temporal and categorical harmonization happens here. Any inability to
        harmonize should return an empty dataset and an error response explaining what went wrong (e.g. not available
        for 'geog' because of privacy reasons)

        Override when necessary.

        :param geogs:
        :param parent_geog_lvl:
        :return:
        """
        """
        Gets a representation of data for the viz.

        If representing the data as a list of records doesn't make sense for the visualization (e.g. maps),
        this method can be overridden.

        :param geogs:
        :return:
        """
        data: list[dict] = []
        for variable in self.variables:
            data += [datum.as_dict() for datum in
                     variable.get_values(geogs, self.time_axis, parent_geog_lvl=parent_geog_lvl)]

        return data

    def _get_viz_options(self, geog: 'AdminRegion') -> Optional[dict]:
        return {}

    class Meta:
        verbose_name = "Data Visualization"
        verbose_name_plural = "Data Visualizations"


# ==================
# +  Map
# ==================
class MiniMap(DataViz):
    BORDER_LAYER_BASE = {
        "type": "line",
        "paint": {
            "line-color": "#333",
            "line-width": [
                "interpolate",
                ["exponential", 1.51],
                ["zoom"],
                0, 1,
                8, 1,
                16, 14
            ]
        },
    }
    vars = models.ManyToManyField('Variable', verbose_name='Layers', through='MapLayer')

    @property
    def layers(self):
        return self.vars.all()

    def _get_viz_data(self, geogs: QuerySet['AdminRegion'],
                      parent_geog_lvl: Optional[Type['AdminRegion']] = None) -> list[dict]:
        return []  # map data is stored in geojson that is served elsewhere

    def _get_viz_options(self, geog: 'AdminRegion', parent_geog_lvl=None) -> dict:
        """
        Collects and returns the data for this presentation at the `geog` provided

        Cross-geography presentations will cached. keyed in part by `type(geog)`
        as the data returned is the same for any target geog of the same type
        """
        sources: [dict] = []
        layers: [dict] = []
        interactive_layer_ids: [str] = []
        legend_options: [dict] = []

        for var in self.vars.all():
            # for each variable/layer, get its data geojson, style and options
            layer: MapLayer = self.vars.through.objects.get(variable=var, viz=self)
            data_layer: DataLayer = layer.get_data_layer(geog_type=type(geog))
            source, tmp_layers, interactive_layer_ids, legend_option = data_layer.get_map_options()
            sources.append(source)
            legend_options.append(legend_option)
            layers += tmp_layers

        map_options: dict = {
            'interactive_layer_ids': interactive_layer_ids,
            'default_viewport': {
                'longitude': geog.geom.centroid.x,
                'latitude': geog.geom.centroid.y,
                'zoom': geog.base_zoom - 3
            }
        }

        # for highlighting current geog
        highlight_id = slugify(geog.name)
        highlight_source = {
            'id': f'{highlight_id}',
            'type': 'geojson',
            'data': geog.simple_geojson,
        }
        highlight_layer = {
            'id': f'{highlight_id}/highlight',
            'source': f'{highlight_id}',
            **self.BORDER_LAYER_BASE
        }
        sources.append(highlight_source)
        layers.append(highlight_layer)

        return {'sources': sources,
                'layers': layers,
                'legends': legend_options,
                'map_options': map_options}

    def __str__(self):
        return self.name


class MapLayer(PolymorphicModel, VizVariable):
    """ Base class for map layers """
    viz = models.ForeignKey('MiniMap', on_delete=models.CASCADE, related_name='mini_map_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_mini_map')

    # options
    visible = models.BooleanField(verbose_name='Visible by default', default=True)
    use_percent = models.BooleanField()

    # mapbox style
    custom_paint = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                    blank=True, null=True)
    custom_layout = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                     blank=True, null=True)

    def get_data_layer(self, geog_type: Type['AdminRegion']):
        return DataLayer.get_or_create_updated_map(geog_type, self.viz.time_axis, self.variable, self.use_percent)


# ==================
# +  Table
# ==================
class Table(DataViz):
    vars = models.ManyToManyField('Variable', verbose_name='Rows', through='TableRow')
    transpose = models.BooleanField(default=False)
    show_percent = models.BooleanField(default=True)

    @property
    def view_height(self):
        return (len(self.vars.all()) // 5) + 4

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH

    @property
    def variables(self):
        return self.vars.order_by('variable_to_table')

    def _get_viz_data(self, geogs: QuerySet['AdminRegion'],
                      parent_geog_lvl: Optional[Type['AdminRegion']] = None) -> list[dict]:
        """ Gets data for each variable across time """
        data_check = []
        results = []
        for variable in self.variables:
            var_data = variable.get_values(geogs, self.time_axis, parent_geog_lvl=parent_geog_lvl)
            data_check += var_data
            time_data = {datum.time: datum.as_value_dict() for datum in var_data}
            results.append({'variable': variable.slug, **time_data})
        if not data_check:
            raise EmptyResultsError('Data not available.')
        return results

    def _get_viz_options(self, geog: 'AdminRegion') -> Optional[dict]:
        columns = [{"Header": '', "accessor": 'variable'}, ] + \
                  [{"Header": tp.name, "accessor": tp.slug} for tp in self.time_axis.time_parts]
        return {'transpose': self.transpose, 'show_percent': self.show_percent, 'columns': columns}


class TableRow(VizVariable):
    viz = models.ForeignKey('Table', on_delete=models.CASCADE, related_name='table_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_table')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


# ==================
# +  Charts
# ==================
class Chart(DataViz):
    """
    Abstract base class for charts
    """
    LINE = 'line'
    SQUARE = 'square'
    RECT = 'rect'
    CIRCLE = 'circle'
    CROSS = 'cross'
    DIAMOND = 'diamond'
    STAR = 'star'
    TRIANGLE = 'triangle'
    WYE = 'wye'
    NONE = 'none'
    LEGEND_TYPE_CHOICES = (
        (LINE, 'Line'),
        (SQUARE, 'Square'),
        (RECT, 'Rectangle'),
        (CIRCLE, 'Circle'),
        (CROSS, 'Cross'),
        (DIAMOND, 'Diamond'),
        (STAR, 'Star'),
        (TRIANGLE, 'Triangle'),
        (WYE, 'Wye'),
        (NONE, 'None'),
    )
    vars = models.ManyToManyField('Variable', verbose_name='Rows', through='ChartPart')
    legend_type = models.CharField(max_length=10, choices=LEGEND_TYPE_CHOICES, default='circle')

    across_geogs = models.BooleanField(
        help_text='Check if you want this chart to compare the statistic '
                  'across geographies instead of across time',
        default=False)

    @property
    def options(self) -> dict:
        return {'across_geogs': self.across_geogs}

    def _get_viz_options(self, geog: 'AdminRegion') -> Optional[dict]:
        return {'legend_type': self.legend_type, 'across_geogs': self.across_geogs}


class ChartPart(VizVariable):
    viz = models.ForeignKey('Chart', on_delete=models.CASCADE, related_name='chart_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_chart')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


# ==================
# +  Alphanumeric
# ==================
class Alphanumeric(DataViz):
    class Meta:
        abstract = True


class BigValueVariable(VizVariable):
    viz = models.ForeignKey('BigValue', on_delete=models.CASCADE, related_name='big_value_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_big_value')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


class BigValue(Alphanumeric):
    PLAIN = 'PLN'
    FRACTION = 'FRN'
    PERCENT = 'PCT'
    BOTH = 'BTH'
    FORMAT_CHOICES = (
        (PLAIN, "Plain"),
        (FRACTION, "Approximate, human friendly, fraction over denominator."),
        (PERCENT, "Percent of denominator"),
        (BOTH, "Number and Fraction"),
    )
    vars = models.ManyToManyField('Variable', through=BigValueVariable)
    note = models.TextField(blank=True, null=True)
    format = models.TextField(max_length=3, choices=FORMAT_CHOICES, default=PLAIN,
                              help_text="Only use percent for numbers with denominators. "
                                        "Variables with 'percent' as a unit should use 'Plain'")

    @property
    def view_width(self):
        return self.width_override or self.DEFAULT_WIDTH


class SentenceVariable(VizVariable):
    viz = models.ForeignKey('Sentence', on_delete=models.CASCADE, related_name='sentence_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_sentence')

    class Meta:
        unique_together = ('viz', 'variable', 'order',)


class Sentence(Alphanumeric):
    vars = models.ManyToManyField('Variable', through=SentenceVariable)
    text = models.TextField(
        help_text='To place a value in your sentence, use {order}. e.g. "There are {1} cats and {2} dogs in town."')

    def get_text_data(self, geog: 'AdminRegion') -> DataResponse:
        data = ''
        error: ErrorResponse
        only_time_part = self.time_axis.time_parts[0]

        if self.can_handle_geography(geog):
            fields = {'geo': geog.title, }
            try:
                for variable in self.vars.all():
                    order = SentenceVariable.objects.filter(alphanumeric=self, variable=variable)[0].order
                    val = variable.get_table_row(self, geog)[only_time_part.slug]['v']
                    fields[f'v{order}'] = f"<strong>{val}</strong>"
                    denoms = variable.denominators.all()
                    if denoms:
                        d_val = variable.get_proportional_datum(geog, only_time_part, denoms[0])
                        fields[f'v{order}d'] = f"{d_val:.2%}"
                data = pystache.render(self.text, fields)
                error = ErrorResponse(level=ErrorLevel.OK, message=None)
            except Exception as e:
                error = ErrorResponse(level=ErrorLevel.ERROR, message=str(e))
        else:
            error = ErrorResponse(level=ErrorLevel.EMPTY,
                                  message=f'This Sentence is not available for {geog.name}.')

        return DataResponse(data=data, error=error)


@receiver(m2m_changed, sender=DataViz.variables, dispatch_uid="check_var_timing")
def check_var_timing(_, instance: DataViz, **kwargs):
    for var in instance.vars.all():
        var: 'Variable'
        for time_part in instance.time_axis.time_parts:
            if not var.can_handle_time_part(time_part):
                raise ValidationError(f'{var.slug} is not available in time {time_part.slug}')
