import logging
import re
from typing import Optional, TYPE_CHECKING, List

from colorama import Fore, Style
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel

from context.models import WithContext, WithTags
from indicators.data import Datum, GeogCollection, GeogRecord
from indicators.errors import AggregationError, DataRetrievalError
from indicators.models import Variable, Source
from indicators.utils import ErrorRecord, DataResponse, ErrorLevel

from profiles.abstract_models import Described
from django.db.models import QuerySet, Manager
from geo.models import AdminRegion

if TYPE_CHECKING:
    from indicators.models.variable import Variable

logger = logging.getLogger(__name__)


class VizVariable(models.Model):
    """ Common fields and methods for all variables attached to data vizes """
    order = models.IntegerField()

    class Meta:
        abstract = True
        ordering = ['order']


class DataViz(PolymorphicModel, WithTags, WithContext, Described):
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
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', self.__class__.__qualname__)
        # noinspection RegExpSimplifiable
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

    @property
    def children(self) -> List[QuerySet]:
        from indicators.models import TimeAxis
        return [self.sources, self.variables, TimeAxis.objects.filter(id=self.time_axis.id)]


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
        """ Generates queryset of all neighbor geographies to be compared with `geog` also includes geog."""
        return geog.__class__.objects.filter(global_geoid=geog.global_geoid)

    def get_viz_data(self, geog: 'AdminRegion') -> DataResponse:
        """
        Returns a `DataResponse` object with the viz's data at `geog`.

        This method is the primary interface to request data. Calls `_get_viz_data` which can be implemented
        in subclassed models.

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
        data: Optional[list[Datum]] = None
        options: Optional[dict] = None
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
                data, warnings = self._get_viz_data(geog_collection)
                options = self._get_viz_options(geog_collection)
            else:
                error = ErrorRecord(level=ErrorLevel.EMPTY,
                                    message=f'This visualization is not available for {geog.name}.')
            return DataResponse(data, options, error, warnings=warnings)

        except DataRetrievalError as e:
            logger.error(str(e))
            error = e.error_response
            return DataResponse(data, options, error, warnings=warnings)

        except Exception as e:
            logger.exception(str(e))
            print(f'{Fore.RED}Uncaught Error:', e, Style.RESET_ALL)
            # error = ErrorResponse(ErrorLevel.ERROR, f'Uncaught Error: {e}')
            raise e
            # return DataResponse(data, options, error)

    def _get_viz_data(self, geog_collection: GeogCollection) -> (list[Datum], list[ErrorRecord]):
        """
        Gets a representation of data for the viz.

        All the nitty-gritty work of spatial, temporal and categorical harmonization happens here. Any inability to
        harmonize should return an empty dataset and an error response explaining what went wrong (e.g. not available
        for 'geog' because of privacy reasons)

        Override when necessary.

        If representing the data as a list of records doesn't make sense for the visualization (e.g. maps),
        this method can be overridden.
        """
        data: list[Datum] = []
        warnings: list[ErrorRecord] = []

        for variable in self.variables:
            var_data, var_warnings = variable.get_values(geog_collection, self.time_axis)
            data += var_data
            warnings += var_warnings

        return data, warnings

    def _get_viz_options(self, geog_collection: GeogCollection) -> Optional[dict]:
        """
        Gets options for the viz.

        Options are particularly class-specific, so you'll need to override in most cases.

        :param geog_collection:
        :return:
        """
        return {}

    def __str__(self):
        return f'{self.name} ({self.__class__.__name__})'

    class Meta:
        verbose_name = "Data Visualization"
        verbose_name_plural = "Data Visualizations"


@receiver(m2m_changed, sender=DataViz.variables, dispatch_uid="check_var_timing")
def check_var_timing(_, instance: DataViz, **kwargs):
    for var in instance.vars.all():
        var: 'Variable'
        for time_part in instance.time_axis.time_parts:
            if not var.can_handle_time_part(time_part):
                raise ValidationError(f'{var.slug} is not available in time {time_part.slug}')
