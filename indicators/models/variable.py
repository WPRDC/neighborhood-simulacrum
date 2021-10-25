import logging
import math
from datetime import MINYEAR, MAXYEAR
from typing import Dict, Optional, Type, List, Union

from django.core.cache import caches
from django.db import models
from django.db.models import QuerySet, Sum, Manager, F, OuterRef, Subquery
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from census_data.models import CensusValue, CensusTableRecord
from geo.models import AdminRegion, CensusGeography
from indicators.data import Datum
from indicators.errors import AggregationError, MissingSourceError, EmptyResultsError
from indicators.models.source import Source, CensusSource, CKANSource, CKANRegionalSource
from indicators.models.time import TimeAxis
from indicators.utils import ErrorLevel
from profiles.abstract_models import Described
from profiles.settings import LONG_TERM_CACHE_TTL, USE_LONG_TERM_CACHE

logger = logging.getLogger(__name__)


class Variable(PolymorphicModel, Described):
    NONE = 'NONE'
    COUNT = 'COUNT'
    SUM = 'SUM'
    MEAN = 'AVG'
    MODE = 'MODE'
    MAX = 'MAX'
    MIN = 'MIN'
    AGGR_CHOICES = (
        (NONE, 'None'),
        (COUNT, 'Count'),
        (SUM, 'Sum'),
        (MEAN, 'Mean'),
        (MODE, 'Mode'),
        (MAX, 'Maximum'),
        (MIN, 'Minimum'),
    )

    _agg_methods: dict

    # todo: currently everything has been built with aggregation in mind.  selecting 'None' will mean that the variable
    #   will return a list and not a single value. Data Presentations may require certain return values or behave
    #   different depending on the variable return type
    _warnings: list[dict] = []

    sources: Manager['Source']
    short_name = models.CharField(max_length=26, null=True, blank=True)

    aggregation_method = models.CharField(
        help_text='Select "None" if this value cannot be used in aggregate.',
        max_length=5,
        choices=AGGR_CHOICES,
        default=SUM,
    )

    units = models.CharField(
        help_text='Special format for $.  Otherwise, displayed after value.',
        max_length=30,
        null=True,
        blank=True
    )
    unit_notes = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    denominators = models.ManyToManyField(
        'Variable',
        help_text='Variables that represent a universe under which the current variable can be analyzed',
        blank=True
    )
    percent_label_text = models.CharField(
        help_text='Label to use when being used as denominator. If not provided, "% of &lt;title&gt;" will be used',
        max_length=100,
        null=True,
        blank=True
    )
    depth = models.IntegerField(
        help_text='Used to represent hierarchy of data. In practice, it is used to indent rows in '
                  'a table corresponding to this variable',
        default=0
    )

    @property
    def display_name(self):
        return self.name

    @property
    def percent_label(self):
        return self.percent_label_text if self.percent_label_text else f'% of {self.name}'

    @property
    def locale_options(self):
        if self.units:
            if self.units[0] == '$':
                return {'style': 'currency', 'currency': 'USD', 'minimumFractionDigits': 0}
            if self.units[0] == '%':
                return {'style': 'percent'}
        return {}

    @property
    def aggregation_method_class(self):
        return {
            self.NONE: models.Sum,
            self.COUNT: models.Count,
            self.SUM: models.Sum,
            self.MEAN: models.Avg,
            self.MAX: models.Max,
            self.MIN: models.Min
        }.get(self.aggregation_method, models.Sum)

    @property
    def source_agg_method(self):
        """ Uses instances subclass's `_agg_methods` to determine what to return. """
        return self._agg_methods[self.aggregation_method]

    @property
    def primary_denominator(self) -> Optional['Variable']:
        denoms = self.denominators.all()
        return denoms[0] if len(denoms) else None

    def get_values(self, geogs: QuerySet['AdminRegion'], time_axis: 'TimeAxis',
                   use_denom=True, parent_geog_lvl: Optional[Type['AdminRegion']] = None) -> list['Datum']:
        """
        Collects data for this `Variable` instance across geographies in `geogs` and times in `time_axis`.
        """
        cache, cache_key = None, None
        agg_method = self.source_agg_method
        using_agg = parent_geog_lvl is not None and type(geogs[0]) != parent_geog_lvl
        if using_agg and agg_method is None:
            raise AggregationError(f"Variable '{self.name}' can't be aggregated.")

        if USE_LONG_TERM_CACHE:
            cache = caches['long_term']
            cache_key = self._generate_cache_key(geogs, time_axis, use_denom=use_denom,
                                                 agg_method=agg_method, parent_geog_lvl=parent_geog_lvl)
            cached_data = cache.get(cache_key)
            if cached_data:
                print('Using cached data', cache_key)
                return cached_data

        data: list[Datum] = self._get_values(geogs, time_axis, use_denom=use_denom,
                                             agg_method=agg_method, parent_geog_lvl=parent_geog_lvl)

        self._check_values(data)

        if USE_LONG_TERM_CACHE and cache and cache_key:
            cache.set(cache_key, data, LONG_TERM_CACHE_TTL)
            print('Cached', cache_key)

        return data

    def _get_values(self, geogs: QuerySet['AdminRegion'], time_axis: 'TimeAxis', use_denom=True,
                    agg_method=None, parent_geog_lvl: Optional[Type['AdminRegion']] = None) -> list['Datum']:
        raise NotImplementedError

    @staticmethod
    def _check_values(data: list[Datum]):
        for datum in data:
            if datum.value is not None:
                continue
            raise EmptyResultsError('No values returned.')

    def _generate_cache_key(self, geogs: QuerySet['AdminRegion'], time_axis: 'TimeAxis', use_denom=True,
                            agg_method=None, parent_geog_lvl: Optional[Type['AdminRegion']] = None):
        geog_key = tuple(sorted((geog.common_geoid for geog in geogs.all())))
        time_key = time_axis.slug
        denom_key = int(use_denom)
        agg_key = str(agg_method)
        pgl_key = str(parent_geog_lvl)
        return str(hash((self.slug, geog_key, time_key, denom_key, agg_key, pgl_key)))

    def can_handle_time_part(self, time_part: TimeAxis.TimePart) -> bool:
        """ Returns `True` if any of a variable instance's sources can can handle `time_part`. """
        for source in self.sources.all():
            if source.can_handle_time_part(time_part):
                return True
        return False

    def can_handle_geography(self, geog: AdminRegion) -> bool:
        """ Returns `True` if any of a variable instance's sources can can handle `geog`. """
        for source in self.sources.all():
            if source.can_handle_geography(geog):
                return True
        return False

    def _add_warning(self, warning: dict):
        self._warnings += [warning]

    def __str__(self):
        return f'{self.name} ({self.slug})'


class CensusVariable(Variable):
    sources = models.ManyToManyField(
        'CensusSource',
        related_name='census_variables',
        through='CensusVariableSource'
    )

    _agg_methods = {
        Variable.NONE: None,
        Variable.COUNT: models.Count,
        Variable.SUM: models.Sum,
        Variable.MEAN: models.Avg,
        Variable.MODE: None,
        Variable.MAX: models.Max,
        Variable.MIN: models.Min,
    }

    def _get_values(self,
                    geogs: QuerySet[Union[AdminRegion, CensusGeography]],
                    time_axis: TimeAxis,
                    use_denom=True,
                    agg_method=None,
                    parent_geog_lvl=None) -> list[Datum]:
        results: list[Datum] = []
        for geog in geogs:
            results += self._get_values_for_geog(geog, time_axis, use_denom)
        return results

    def _get_values_for_geog(self,
                             geog: Union[AdminRegion, CensusGeography],
                             time_axis: TimeAxis, use_denom=True) -> list[Datum]:
        """ Retrieves data for the variable instance at the geography `geog` """
        # get the census/acs tables for the points in time_axis
        census_table_records_by_year = self.get_census_table_records_for_time_axis(time_axis)
        denom_census_table_records_by_year: Dict[str, QuerySet[CensusTableRecord]] = {}
        if use_denom:
            denoms = self.denominators.all()
            denom_census_table_records_by_year = denoms[0].get_census_table_records_for_time_axis(
                time_axis) if denoms else {}

        # extract and compute the values at each point in time_axis
        results = []
        for time_part_slug, records in census_table_records_by_year.items():
            # extract IDs
            value_ids, moe_ids = CensusTableRecord.get_table_uids(records)
            val = CensusValue.objects.filter(
                geog_uid=geog.affgeoid,
                census_table_uid__in=value_ids
            ).values('geog_uid').annotate(val=Sum('value')).values('val')[0]['val']

            if len(moe_ids) == 1:
                # https://www.census.gov/content/dam/Census/library/publications/2018/acs/acs_general_handbook_2018_ch08.pdf
                moe_results = CensusValue.objects.filter(
                    geog_uid=geog.affgeoid,
                    census_table_uid__in=moe_ids
                ).annotate(
                    moe=(F('value') ** 2.0)
                ).values('moe').values('moe')
                moe: Optional[float] = math.sqrt(sum(result['moe'] for result in moe_results))
            else:
                self._add_warning(
                    {'message': 'Margins of Error for compound variables cannot be accurately reported at this time.'})
                moe = None

            # if denom is being used, look up the corresponding record and get its value
            denom, percent = None, None
            if use_denom and time_part_slug in denom_census_table_records_by_year:
                denom_record = denom_census_table_records_by_year[time_part_slug]
                denom_ids, _ = CensusTableRecord.get_table_uids(denom_record)
                denom = CensusValue.objects.filter(
                    geog_uid=geog.affgeoid,
                    census_table_uid__in=denom_ids
                ).values('geog_uid').annotate(denom=Sum('value')).values('denom')[0]['denom']
                if denom and denom > 0:
                    percent = val / denom

            results.append(Datum(variable=self.slug, time=time_part_slug, geog=geog.common_geoid,
                                 value=val, moe=moe, denom=denom, percent=percent))
        return results

    # Utils
    def _get_source_for_time_point(self, time_point: timezone.datetime) -> 'CensusSource':
        """ Find instance's source that covers time_point"""
        is_decade = not time_point.year % 10
        dataset = 'CEN' if is_decade else 'ACS5'
        return self.sources.filter(
            dataset=dataset,
            time_coverage_start__lte=time_point,
            time_coverage_end__gte=time_point,
        )[0]

    def _get_census_table_record_for_time_part(self, time_part: 'TimeAxis.TimePart') -> QuerySet['CensusTableRecord']:
        """
        Returns a queryset that represents all `CensusTableRecord`s (value and moe tables) related to `time_part`.
        """
        source = self._get_source_for_time_point(time_part.time_point)
        return CensusVariableSource.objects.get(variable=self, source=source).census_table_records.all()

    def get_census_table_records_for_time_axis(self, time_axis: 'TimeAxis') -> Dict[str, QuerySet['CensusTableRecord']]:
        """
        Return a dict mapping time_parts, by slug, to the queryset of CensusTableRecords associated with that time_part.
        """
        data = {}
        for time_part in time_axis.time_parts:
            data[time_part.slug] = self._get_census_table_record_for_time_part(time_part)
        return data


class CKANVariable(Variable):
    sources = models.ManyToManyField(
        'CKANSource',
        related_name='ckan_variables',
    )
    field = models.CharField(
        help_text='field in source to aggregate',
        max_length=100
    )
    sql_filter = models.TextField(help_text='SQL clause that will be used to filter data.', null=True, blank=True)

    _agg_methods = {
        Variable.NONE: None,
        Variable.COUNT: 'COUNT',
        Variable.SUM: 'SUM',
        Variable.MEAN: 'AVG',
        Variable.MODE: None,
        Variable.MAX: 'MAX',
        Variable.MIN: 'MIN',
    }

    def _get_values(self, geogs: QuerySet['AdminRegion'], time_axis: 'TimeAxis', use_denom=True, agg_method=None,
                    parent_geog_lvl=None) -> list[Datum]:
        results: list[Datum] = []

        for time_part in time_axis.time_parts:
            source: CKANSource = self._get_source_for_time_part(time_part)
            denom_select, denom_data = self._get_denom_data(source, geogs, time_part) if use_denom else (None, None)

            # get the raw data for this geog and time_part from CKAN
            query = source.get_data_query(self, geogs, time_part, parent_geog_lvl=parent_geog_lvl,
                                          denom_select=denom_select)

            # get data from ckan and wrap it in our Datum class
            raw_data: list[dict] = source.query_datastore(query)
            var_data: list[Datum] = Datum.from_ckan_response_data(self, raw_data)
            print(var_data)
            # todo: build aggregation below into the query

            # for regional sources, we need to aggregate here for now todo: debug whats up with ckan's SQL API
            if parent_geog_lvl and type(source) == CKANRegionalSource:
                var_data = self._aggregate_data(var_data, type(geogs[0]), parent_geog_lvl)
                if denom_data:
                    denom_data = self._aggregate_data(denom_data, type(geogs[0]), parent_geog_lvl)

            if denom_data:
                # we need to link the data
                results += self._join_data(var_data, denom_data)
            else:
                # either no denom at all, or denom was in same source, and captured using `denom_select`
                results += var_data

        return results

    @property
    def agg_str(self):
        return '' if self.aggregation_method == self.NONE else self.aggregation_method

    # Utils
    @staticmethod
    def _join_data(var_data: List[Datum], denom_data: List[Datum]):
        """ Adds denom value to appropriate datum in response data """
        denom_lookup: dict[str, Optional[float]] = {f'{d.geog}/{d.time}': d.value for d in denom_data}
        return [v.with_denom_val(denom_lookup[f'{v.geog}/{v.time}']) for v in var_data]

    def _aggregate_data(self, data: list[Datum], base_geog_lvl: Type[AdminRegion],
                        parent_geog_lvl: Type[AdminRegion]) -> list[Datum]:
        """ Rolls up data to `parent_geog_lvl` using `self.aggregation_method` """
        # join parent join to base_geogs
        parent_sq = Subquery(parent_geog_lvl.objects.filter(geom__covers=OuterRef('geom')).values('common_geoid'))
        # filter to geoids found in data
        lookup_geogs: QuerySet[AdminRegion] = base_geog_lvl.objects.filter(
            common_geoid__in=[d.geog for d in data]
        ).annotate(parent_geoid=parent_sq)
        # make lookup dict from queryset
        lookup = {geog.common_geoid: geog.parent_geoid for geog in lookup_geogs}
        # using lookup, replace each datum's geog with the parent one
        # todo roll up data to parent geog
        joined_data = [datum.update(geog=lookup[datum.geog]) for datum in data]

        # split data by parent_geog
        parent_data = {}
        for datum in joined_data:
            if datum.geog not in parent_data:
                parent_data[datum.geog] = {datum.time: [datum]}
            else:
                if datum.time in parent_data[datum.geog]:
                    parent_data[datum.geog][datum.time] += [datum]
                else:
                    parent_data[datum.geog][datum.time] = [datum]

        results: list[Datum] = []
        for geog, time_record in parent_data.items():
            for time, data in time_record.items():
                values = [d.value for d in data]
                denoms = [d.denom for d in data]
                if None in values:
                    raise AggregationError(f"Cannot aggregate data for '{geog}' since data is not available for all of "
                                           f"its constituent '{base_geog_lvl.geog_type}'s.")
                if None in denoms:
                    self._add_warning({'level': ErrorLevel.WARNING,
                                       'message': f"Cannot aggregate denominator data for '{geog}' at '{time}' "
                                                  f"since data is not available for "
                                                  f"all of its constituent '{base_geog_lvl.geog_type}'s"})
                value = sum(values)
                denom = sum(denoms) if len(denoms) and None not in denoms else None
                percent = value / denom if denom else None
                results.append(
                    Datum(variable=self.slug, geog=geog, time=time, value=value, denom=denom, percent=percent))
        return results

    def _get_source_for_time_part(self, time_part: TimeAxis.TimePart) -> Optional[CKANSource]:
        """ Return CKAN source that covers the time in `time_point` """
        # fixme: we'll need to come up with a more correct way of doing this: maybe a `through` relationship
        source: CKANSource
        for source in self.sources.all():
            # go through the sources and get the first one whose range covers the point
            start = source.time_coverage_start if source.time_coverage_start else timezone.datetime(MINYEAR, 1, 1)
            end = source.time_coverage_end if source.time_coverage_end else timezone.datetime(MAXYEAR, 12, 31)
            if start <= time_part.time_point < end:
                return source
        raise MissingSourceError(f'No source found for `{self.slug}` for time period `{time_part.slug}`.')

    def _get_denom_data(self, source: 'CKANSource', geogs: QuerySet['AdminRegion'],
                        time_part: 'TimeAxis.TimePart') -> tuple[str, list[Datum]]:
        # check for denominator and handle
        denom_var: 'CKANVariable' = self.primary_denominator
        denom_select = None
        denom_data: list[Datum] = []
        if denom_var:
            if len(denom_var.sources.filter(pk=source.pk)):
                # if denom uses the same source we can simply pass its field select
                denom_select = f'{denom_var.agg_str}("{denom_var.field}")'
            else:
                # if not, keep the denom select null , but fire off a call to collect
                denom_source = denom_var._get_source_for_time_part(time_part)
                denom_query = denom_source.get_data_query(denom_var, geogs, time_part)
                denom_data = Datum.from_ckan_response_data(denom_var, source.query_datastore(denom_query))

        return denom_select, denom_data


class CensusVariableSource(models.Model):
    """ for linking Census variables to their sources while keeping track of the census formula format for that combo"""
    variable = models.ForeignKey('CensusVariable', on_delete=models.CASCADE, related_name='variable_to_source')
    source = models.ForeignKey('CensusSource', on_delete=models.CASCADE, related_name='source_to_variable')
    census_table_records = models.ManyToManyField('census_data.CensusTableRecord')

    class Meta:
        index_together = ('variable', 'source',)
        unique_together = ('variable', 'source',)
