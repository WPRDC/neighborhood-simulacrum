import dataclasses
from dataclasses import dataclass
from datetime import MINYEAR, MAXYEAR
from typing import Dict, Optional, Type, List

import requests
from django.db import models
from django.core.cache import caches
from django.db.models import QuerySet, Sum, Manager, F, OuterRef, Subquery, Value, Case, When
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from census_data.models import CensusValue, CensusTable, CensusTablePointer
from geo.models import CensusGeography
from indicators.errors import AggregationError, MissingSourceError, EmptyResultsError
from indicators.models.abstract import Described
from indicators.models.source import Source, CensusSource, CKANSource, CKANRegionalSource, DENOM_DKEY, \
    VALUE_DKEY, TIME_DKEY, GEOG_DKEY
from indicators.models.time import TimeAxis
from indicators.models.viz import DataViz
from indicators.utils import ErrorLevel, limit_to_geo_extent

# todo: move to settings
CKAN_API_BASE_URL = 'https://data.wprdc.org/api/3/'
DATASTORE_SEARCH_SQL_ENDPOINT = 'action/datastore_search_sql'

LT_CACHE_TTL = 60 * 60 * 24  # 24 hours


@dataclass
class Datum:
    variable: str
    geog: str
    time: str
    value: Optional[float] = None
    moe: Optional[float] = None
    percent: Optional[float] = None
    denom: Optional[float] = None

    @staticmethod
    def from_census_response_datum(variable: 'CensusVariable', census_datum) -> 'Datum':
        return Datum(
            variable=variable.slug,
            geog=census_datum.get('geog'),
            time=census_datum.get('time'),
            value=census_datum.get('value'),
            moe=census_datum.get('moe'),
            denom=census_datum.get('denom'),
            percent=census_datum.get('percent'), )

    @staticmethod
    def from_census_response_data(variable: 'CensusVariable', census_data: list[dict]) -> List['Datum']:
        return [Datum.from_census_response_datum(variable, census_datum) for census_datum in census_data]

    @staticmethod
    def from_ckan_response_datum(variable: 'CKANVariable', ckan_datum) -> 'Datum':
        denom, percent = None, None
        if DENOM_DKEY in ckan_datum:
            denom = ckan_datum[DENOM_DKEY]
            percent = (ckan_datum[VALUE_DKEY] / ckan_datum[DENOM_DKEY])

        return Datum(variable=variable.slug,
                     geog=ckan_datum[GEOG_DKEY],
                     time=ckan_datum[TIME_DKEY],
                     value=ckan_datum[VALUE_DKEY],
                     denom=denom,
                     percent=percent)

    @staticmethod
    def from_ckan_response_data(variable: 'CKANVariable', ckan_data: list[dict]) -> List['Datum']:
        return [Datum.from_ckan_response_datum(variable, ckan_datum) for ckan_datum in ckan_data]

    def update(self, **kwargs):
        """ Creates new Datum similar to the instance with new values from kwargs """
        return Datum(**{**self.as_dict(), **kwargs})

    def with_denom_val(self, denom_val: Optional[float]):
        """ Merge the denom value and generate the percent """
        return dataclasses.replace(self, denom=denom_val, percent=(self.value / denom_val))

    def as_dict(self):
        return {'variable': self.variable, 'geog': self.geog, 'time': self.time,
                'value': self.value, 'moe': self.moe, 'percent': self.percent, 'denom': self.denom}

    def as_value_dict(self):
        return {'value': self.value, 'moe': self.moe, 'percent': self.percent, 'denom': self.denom}


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

    # todo: currently everything has been built with aggregation in mind.  selecting 'None' will mean that the variable
    #   will return a list and not a single value. Data Presentations may require certain return values or behave
    #   different depending on the variable return type
    _warnings: list[dict] = []

    sources: Manager['Source']
    short_name = models.CharField(max_length=26, null=True, blank=True)

    aggregation_method = models.CharField(
        max_length=5,
        choices=AGGR_CHOICES,
        default=SUM,
    )

    units = models.CharField(
        help_text='Special format for $.  Otherwise, often displayed after value.',
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
    def primary_denominator(self) -> Optional['Variable']:
        denoms = self.denominators.all()
        return denoms[0] if len(denoms) else None

    def get_values(self, geogs: QuerySet['CensusGeography'], time_axis: 'TimeAxis', use_denom=True,
                   agg_method=None, parent_geog_lvl: Optional[Type['CensusGeography']] = None) -> list['Datum']:
        """
        Collects data for this `Variable` instance across geographies in `geogs` and times in `time_axis`.

        :param parent_geog_lvl:
        :param {QuerySet['CensusGeography']} geogs: a QuerySet for the geographies being explored.
        :param {TimeAxis} time_axis: the points in times being explored
        :param {Aggregate} agg_method: aggregate function to perform on data after filtering by geography and time
        :param {bool} use_denom: whether or not to also gather percent and denominator data
        :return:
        """
        cache = caches['long_term']
        cache_key = self._generate_cache_key(geogs, time_axis, use_denom=use_denom, agg_method=agg_method,
                                             parent_geog_lvl=parent_geog_lvl)
        cached_data = cache.get(cache_key)
        if cached_data:
            print('Using cached data', cache_key)
            return cached_data
        data: list[Datum] = self._get_values(geogs, time_axis, use_denom=use_denom, agg_method=agg_method,
                                             parent_geog_lvl=parent_geog_lvl)

        self._check_values(data)

        cache.set(cache_key, data, LT_CACHE_TTL)
        print('Cached', cache_key)
        return data

    def get_primary_value(self, geog: 'CensusGeography', time_part: 'TimeAxis.TimePart') -> Optional[float]:
        geogs, use_agg = self._get_geog_queryset(geog)
        parent_geog_lvl = type(geog) if use_agg else None
        time_axis = TimeAxis.from_time_parts([time_part])
        values = self.get_values(geogs, time_axis, parent_geog_lvl=parent_geog_lvl)
        return values[0].value if len(values) else None

    def _get_geog_queryset(self, geog: 'CensusGeography') -> tuple[Optional[QuerySet['CensusGeography']], bool]:
        # check how geog works for this viz
        # does it work directly for the goeg?
        if self.can_handle_geography(geog):
            return type(geog).objects.filter(pk=geog.pk), False

        # does it work as an aggregate over a smaller geog?
        for child_geog_model in geog.child_geog_models:
            child_geogs = child_geog_model.objects.filter(geom__coveredby=geog.geom)
            if self.can_handle_geographies(child_geogs):
                return child_geogs, True

    def _get_values(self, geogs: QuerySet['CensusGeography'], time_axis: 'TimeAxis', use_denom=True,
                    agg_method=None, parent_geog_lvl: Optional[Type['CensusGeography']] = None) -> list['Datum']:
        raise NotImplementedError

    @staticmethod
    def _check_values(data: list[Datum]):
        for datum in data:
            if datum.value is not None:
                continue
            raise EmptyResultsError('No values returned.')

    def _generate_cache_key(self, geogs: QuerySet['CensusGeography'], time_axis: 'TimeAxis', use_denom=True,
                            agg_method=None, parent_geog_lvl: Optional[Type['CensusGeography']] = None):
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

    def can_handle_geography(self, geog: CensusGeography) -> bool:
        """ Returns `True` if any of a variable instance's sources can can handle `geog`. """
        for source in self.sources.all():
            if source.can_handle_geography(geog):
                return True
        return False

    def _add_warning(self, warning: dict):
        self._warnings += [dict]

    def __str__(self):
        return f'{self.name} ({self.slug})'


class CensusVariable(Variable):
    sources = models.ManyToManyField(
        'CensusSource',
        related_name='census_variables',
        through='CensusVariableSource'
    )

    def _get_values(self, geogs, time_axis, use_denom=True, agg_method=None, parent_geog_lvl=None) -> list[Datum]:
        if not agg_method:
            # todo: make unified agg method class to share between sources
            agg_method = Sum

        if not parent_geog_lvl:
            if len(geogs) == 1:
                parent_geog_lvl = geogs[0]
            else:
                parent_geog_lvl = type(geogs[0])

        # gather all censustables (roll up variables and time)
        census_table_ptrs_by_year = self.get_census_table_ptrs_for_time_axis(time_axis)
        denom_census_table_ptrs_by_year = {}

        if use_denom:
            denoms = self.denominators.all()
            denom_census_table_ptrs_by_year = denoms[0].get_census_tables_for_time_axis(
                time_axis) if denoms else {}

        results = []
        for time_part_slug, census_table_ptrs in census_table_ptrs_by_year.items():
            value_ids, moe_ids = [], []

            # extract IDs
            for ctp in census_table_ptrs:
                value_ids.append(ctp.value_table.id)
                if ctp.moe_table:
                    moe_ids.append(ctp.moe_table.id)

            # Sub queries to get data -
            val_sq = Subquery(CensusValue.objects.filter(
                geography__common_geoid=OuterRef('common_geoid'),
                census_table__in=value_ids
            ).values('geography__common_geoid').annotate(val=agg_method('value')).values('val'))

            if len(moe_ids) == 1:
                # margins come pre-squared for aggregation
                # https://www.census.gov/content/dam/Census/library/publications/2018/acs/acs_general_handbook_2018_ch08.pdf
                pre_moe_sq = Subquery(CensusValue.objects.filter(
                    geography__common_geoid=OuterRef('common_geoid'),
                    census_table__in=moe_ids
                ).annotate(val=(F('value') ** 2.0)).values('val'))
                moe_sq = Sum('pre_moe') ** 0.5
            else:
                self._add_warning(
                    {'message': 'Margins of Error for compoound variables cannot be accurately reported at this time.'})
                pre_moe_sq = Value(None, output_field=models.FloatField(null=True))
                moe_sq = Value(None, output_field=models.FloatField(null=True))

            denom_available = use_denom and time_part_slug in denom_census_table_ptrs_by_year
            if denom_available:
                pre_denom_sq = Subquery(CensusValue.objects.filter(
                    geography__common_geoid=OuterRef('common_geoid'),
                    census_table__in=denom_census_table_ptrs_by_year[time_part_slug]
                ).values('geography__common_geoid').annotate(val=agg_method('value')).values('val'))

                denom_sq = Sum('pre_denom')
                percent_sq = Case(
                    When(denom=0, then=None),
                    default=F('value') / F('denom')
                )

            else:
                pre_denom_sq = Value(None, output_field=models.FloatField(null=True))
                denom_sq = Value(None, output_field=models.FloatField(null=True))
                percent_sq = Value(None, output_field=models.FloatField(null=True))

            # subquery to add parent geog, or just the same geog if no aggregation happening
            if isinstance(parent_geog_lvl, type):
                parent_geog_lvl: Type[CensusGeography]
                # find parent geog that covers the child geog
                parent_geog_sq = Subquery(parent_geog_lvl.objects.filter(
                    geom__covers=OuterRef('geom')).values('common_geoid'))
            elif isinstance(parent_geog_lvl, CensusGeography):
                parent_geog_lvl: CensusGeography
                # if just for one parent geog, save time by just applying it as value
                parent_geog_sq = Value(parent_geog_lvl.common_geoid)
            else:
                raise TypeError(f'`parent_geog_lvl` must be a `CensusGeography` instance or model. '
                                f'Got {type(parent_geog_lvl)} instead.')

            # annotate geogs with all the data and add to results
            data = geogs.annotate(
                geog=parent_geog_sq,
                pre_val=val_sq,
                pre_moe=pre_moe_sq,
                pre_denom=pre_denom_sq,
                time=Value(time_part_slug, output_field=models.CharField())
            ).values(
                'geog'  # rollup by geog
            ).annotate(
                # add aggregate values
                time=F('time'),
                value=Sum('pre_val'),
                moe=moe_sq,  # sqrt of sum of squared MOEs
                denom=denom_sq,
            ).order_by().annotate(
                percent=percent_sq
            ).values('geog', 'time', 'value', 'moe', 'denom', 'percent')
            results += [Datum.from_census_response_datum(self, datum) for datum in data.all()]

        return results

    def _get_values_over_geog_type(self, geog_type, time_part):
        geogs = geog_type.objects.all()
        # queryset of relevant census tables
        census_tables = self.get_census_tables_for_time_part(time_part)
        # get values for all geogs at time, group by geog and sum values
        qs = CensusValue.objects.filter(geography__common_geoid__in=geogs, census_table__in=census_tables).values(
            "geography__common_geoid").annotate(value=Sum('value'))
        return {g['geography__common_geoid']: g['value'] for g in qs.all()}

    # Utils
    def _get_source_for_time_point(self, time_point: timezone.datetime) -> 'CensusSource':
        is_decade = not time_point.year % 10
        if is_decade:
            return self.sources.filter(dataset='CEN')[0]
        return self.sources.filter(dataset='ACS5')[0]  # fixme to handle actual cases

    def get_census_tables_for_time_part(self, time_part: 'TimeAxis.TimePart') -> QuerySet['CensusTable']:
        """
        Returns a queryset that represents all value `CensusTable`s related to `time_part`.

        :param {TimeAxis.TimePart} time_part: the `time_part` by which the `CensusTable`s are filtered
        :return:
        """
        census_table_ptrs = self._get_census_ptr_for_time_part(time_part)
        return CensusTable.objects.filter(value_to_pointer__in=census_table_ptrs)

    def get_census_tables_for_time_axis(self, time_axis: 'TimeAxis') -> Dict[str, QuerySet['CensusTable']]:
        data = {}
        for time_part in time_axis.time_parts:
            data[time_part.slug] = self.get_census_tables_for_time_part(time_part)
        return data

    def _get_census_ptr_for_time_part(self, time_part: 'TimeAxis.TimePart') -> QuerySet['CensusTablePointer']:
        """
        Returns a queryset that represents all `CensusTablePointer`s (value and margin of error) related to `time_part`.

        :param time_part:
        :return:
        """
        source = self._get_source_for_time_point(time_part.time_point)
        return source.source_to_variable.get(variable=self).census_table_pointers.all()

    def get_census_table_ptrs_for_time_axis(self,
                                            time_axis: 'TimeAxis') -> Dict[str, QuerySet['CensusTablePointer']]:
        data = {}
        for time_part in time_axis.time_parts:
            data[time_part.slug] = self._get_census_ptr_for_time_part(time_part)
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

    def _get_values(self, geogs: QuerySet['CensusGeography'], time_axis: 'TimeAxis', use_denom=True, agg_method=None,
                    parent_geog_lvl=None) -> list[Datum]:
        results: list[Datum] = []

        for time_part in time_axis.time_parts:
            source: CKANSource = self._get_source_for_time_part(time_part)
            denom_select, denom_data = self._get_denom_data(source, geogs, time_part) if use_denom else (None, None)

            # get the raw data for this geog and time_part from CKAN
            query = source.get_data_query(self, geogs, time_part, parent_geog_lvl=parent_geog_lvl,
                                          denom_select=denom_select)
            # encode it in Datum objects asap
            var_data: list[Datum] = self._query_datastore(query)

            # for regional sources, we need to aggregate here for now todo: debug whats up with ckan's SQL API
            if parent_geog_lvl and type(source) == CKANRegionalSource:
                var_data = self._aggregate_data(var_data, type(geogs[0]), parent_geog_lvl, agg_method=None)
                if denom_data:
                    denom_data = self._aggregate_data(denom_data, type(geogs[0]), parent_geog_lvl, agg_method=None)

            if denom_data:
                # we need to link the data
                results += self._join_data(var_data, denom_data)
            else:
                # either no denom at all, or denom was in same source, and captured using `denom_select`
                results += var_data

        return results

    # Utils
    def _query_datastore(self, query: str) -> list[Datum]:
        url = CKAN_API_BASE_URL + DATASTORE_SEARCH_SQL_ENDPOINT
        r = requests.post(
            url,
            json={'sql': query},
            headers={
                'Cache-Control': 'no-cache'
            }
        )
        response = r.json()
        data = response['result']['records']
        return Datum.from_ckan_response_data(self, data)

    @staticmethod
    def _join_data(var_data: List[Datum], denom_data: List[Datum]):
        """ Adds denom value to appropriate datum in response data """
        denom_lookup: dict[str, Optional[float]] = {f'{d.geog}/{d.time}': d.value for d in denom_data}
        return [v.with_denom_val(denom_lookup[f'{v.geog}/{v.time}']) for v in var_data]

    def _aggregate_data(self, data: list[Datum], base_geog_lvl: Type[CensusGeography],
                        parent_geog_lvl: Type[CensusGeography], agg_method=None) -> list[Datum]:
        """ Rolls up data to `parent_geog_lvl` using `self.aggregation_method` """
        # join parent join to base_geogs
        parent_sq = Subquery(parent_geog_lvl.objects.filter(geom__covers=OuterRef('geom')).values('common_geoid'))
        # filter to geoids found in data
        lookup_geogs: QuerySet[CensusGeography] = base_geog_lvl.objects.filter(
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
                                           f"its constituent '{base_geog_lvl.TYPE}'s.")
                if None in denoms:
                    self._add_warning({'level': ErrorLevel.WARNING,
                                       'message': f"Cannot aggregate denominator data for '{geog}' at '{time}' "
                                                  f"since data is not available for "
                                                  f"all of its constituent '{base_geog_lvl.TYPE}'s"})
                value = sum(values)
                denom = sum(denoms) if len(denoms) and None not in denoms else None
                percent = value / denom if denom else None
                results.append(Datum(variable=self, geog=geog, time=time, value=value, denom=denom, percent=percent))
        return results

    def _get_source_for_time_part(self, time_part: TimeAxis.TimePart) -> Optional[CKANSource]:
        """ Return CKAN source that covers the time in `time_point` """
        # fixme: we'll need to come up with a more correct way of doing this: maybe a `through` relationship
        source: CKANSource
        for source in self.sources.all():
            # go through the sources and get the first one whose range covers the point
            start = source.time_coverage_start if source.time_coverage_start else timezone.datetime(MINYEAR, 1, 1)
            end = source.time_coverage_end if source.time_coverage_end else timezone.datetime(MAXYEAR, 12, 31)
            if start < time_part.time_point < end:
                return source
        raise MissingSourceError(f'No source found for `{self.slug}` for time period `{time_part.slug}`.')

    def _get_denom_data(self, source: 'Source', geogs: QuerySet['CensusGeography'],
                        time_part: 'TimeAxis.TimePart') -> tuple[str, list[Datum]]:
        # check for denominator and handle
        denom_var: 'CKANVariable' = self.primary_denominator
        denom_select = None
        denom_data: list[Datum] = []
        if denom_var:
            if len(denom_var.sources.filter(pk=source.pk)):
                # if denom uses the same source we can simply pass its field select
                denom_select = self._get_value_select_sql(denom_var)
            # if not, keep the denom select null , but fire off a call to collect
            denom_source = denom_var._get_source_for_time_part(time_part)
            denom_query = denom_source.get_data_query(denom_var, geogs, time_part)
            denom_data = self._query_datastore(denom_query)

        return denom_select, denom_data


# Through models
# =-=-=-=-=-=-=-
class CensusVariableSource(models.Model):
    """ for linking Census variables to their sources while keeping track of the census formula format for that combo"""
    variable = models.ForeignKey('CensusVariable', on_delete=models.CASCADE, related_name='variable_to_source')
    source = models.ForeignKey('CensusSource', on_delete=models.CASCADE, related_name='source_to_variable')
    census_table_pointers = models.ManyToManyField('census_data.CensusTablePointer')
