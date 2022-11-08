import itertools
import logging
import math
import statistics
from datetime import MINYEAR, MAXYEAR
from typing import Dict, Optional, Type, List, Union

from django.db import models
from django.db.models import QuerySet, Sum, Manager, F, OuterRef, Subquery
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from census_data.models import CensusValue, CensusTableRecord
from context.models import WithContext, WithTags
from geo.models import AdminRegion
from indicators.data import Datum, GeogRecord, GeogCollection, AggregationMethod
from indicators.errors import AggregationError, MissingSourceError, EmptyResultsError
from indicators.models.data import CachedIndicatorData
from indicators.models.source import Source, CensusSource, CKANSource, CKANRegionalSource
from indicators.models.time import TimeAxis
from indicators.utils import ErrorLevel, ErrorRecord
from profiles.abstract_models import Described

logger = logging.getLogger(__name__)


def find_missing_geogs_and_time_parts(
        records: Union[QuerySet['CachedIndicatorData'], list['Datum']],
        geog_collection: GeogCollection,
        time_axis: TimeAxis,
) -> ['AdminRegion', 'TimeAxis.TimePart']:
    cached_combos: dict[str, dict[str, bool]] = {}
    missing_geogs: set['AdminRegion'] = set()
    missing_time_parts: set['TimeAxis.TimePart'] = set()

    using_datum = type(records) == list

    for record in records:
        g_key = record.geog.global_geoid if using_datum else record.geog
        t_key = record.time.storage_hash if using_datum else record.time_part_hash
        if g_key not in cached_combos:
            cached_combos[g_key] = {t_key: True}
        else:
            cached_combos[g_key][t_key] = True

    # enumerate possible combinations and check status in trie
    for combo in itertools.product(geog_collection.all_geogs, time_axis.time_parts):
        g: 'AdminRegion' = combo[0]
        t: 'TimeAxis.TimePart' = combo[1]
        if g.global_geoid not in cached_combos or not cached_combos[g.global_geoid][t.storage_hash]:
            missing_geogs.add(g)
            missing_time_parts.add(t)

    return missing_geogs, missing_time_parts


class Variable(PolymorphicModel, Described, WithTags, WithContext):
    _agg_methods: dict
    _warnings: list[ErrorRecord] = []

    sources: Manager['Source']
    short_name = models.CharField(max_length=26, null=True, blank=True)

    aggregation_method: AggregationMethod = models.CharField(
        help_text='Used when having to describe a geography by combining values from smaller geographies. '
                  'Select "None" if this value cannot be used in aggregate functions.',
        max_length=5,
        choices=AggregationMethod.choices,
        default=AggregationMethod.SUM,
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
    def number_format_options(self):
        if self.units:
            if self.units[0] == '$':
                return {'style': 'currency', 'currency': 'USD', 'minimumFractionDigits': 0}
            if self.units[0] == '%':
                return {'style': 'percent'}
        return {}

    @property
    def aggregation_method_class(self):
        return {
            AggregationMethod.NONE: models.Sum,
            AggregationMethod.COUNT: models.Count,
            AggregationMethod.SUM: models.Sum,
            AggregationMethod.MEAN: models.Avg,
            AggregationMethod.MAX: models.Max,
            AggregationMethod.MIN: models.Min
        }.get(self.aggregation_method, models.Sum)

    @property
    def aggregation_method_fn(self):
        return {
            AggregationMethod.NONE: sum,
            AggregationMethod.COUNT: len,
            AggregationMethod.SUM: sum,
            AggregationMethod.MEAN: statistics.mean,
            AggregationMethod.MAX: min,
            AggregationMethod.MIN: max
        }.get(self.aggregation_method, models.Sum)

    @property
    def source_agg_method(self):
        """ Uses instances subclass's `_agg_methods` to determine what to return. """
        return self._agg_methods[self.aggregation_method]

    @property
    def primary_denominator(self) -> Optional['Variable']:
        denoms = self.denominators.all()
        return denoms[0] if len(denoms) else None

    def get_values(
            self,
            geog_collection: GeogCollection,
            time_axis: 'TimeAxis',
            use_denom=True
    ) -> (list['Datum'], list[ErrorRecord]):
        """
        Collects data for this `Variable` instance across geographies in `geogs` and times in `time_axis`.

        :returns: a flat list of Datums of length len(time_axis) * len(geog_collection)
        """
        print()
        using_denom: bool = use_denom
        if use_denom and not len(self.denominators.all()):
            print("!! `use_denom` set but there are no denominators !!")
            using_denom = False

        # since time_points can be kinda ephemeral, they'll be referenced via hash instead of id
        time_part_hash_lookup: dict[str, 'TimeAxis.TimePart'] = {tp.storage_hash: tp for tp in time_axis.time_parts}
        time_part_hashes = list(time_part_hash_lookup.keys())

        # query indicator datastore for any cached results
        cached_data = CachedIndicatorData.objects.filter(
            variable=self.slug,
            geog__in=[sg.global_geoid for sg in geog_collection.all_geogs],
            time_part_hash__in=time_part_hashes,
        )
        result_data: list[Datum] = Variable._datums_from_indicator_caches(cached_data, time_part_hash_lookup)

        # find out if any of the geogs we need data for
        missing_geogs, missing_time_parts = find_missing_geogs_and_time_parts(
            cached_data,
            geog_collection,
            time_axis,
        )

        if missing_geogs and len(missing_geogs) > (len(geog_collection.all_geogs) / 2):
            print('👋 apparently missing data for', missing_geogs)
            # generate temporary geog_collection and time_axis for the missing data
            # to send to source-specific value getter
            temp_geog_collection = GeogCollection(
                geog_type=geog_collection.geog_type,
                primary_geog=geog_collection.primary_geog,
                geographic_extent=geog_collection.geographic_extent
            )
            # add records to geog collection by finding subgeogs
            temp_geog_collection.records = geog_collection.filter_records_by_subgeog_ownership(missing_geogs)

            temp_time_axis = TimeAxis.from_time_parts(list(missing_time_parts))

            # get missing data using source specific queries
            found_data: list[Datum] = self._get_values(
                temp_geog_collection,
                temp_time_axis,
                use_denom=using_denom,
                agg_method=self.source_agg_method,
            )

            # load the missing data into the store for future reuse
            CachedIndicatorData.save_records(found_data)
            # combine cached and recently-collected data to final result
            result_data += found_data

        # check data will raise any exception if there are any errors
        warnings = self._check_values(result_data) + self._warnings
        return result_data, warnings

    def _get_values(
            self,
            geog_collection: GeogCollection,
            time_axis: 'TimeAxis',
            use_denom=True,
            agg_method=None,
    ) -> list['Datum']:
        """
        Implemented by source-specific subclasses

        :returns a flat list of Datums of length len(time_axis) * len(geog_collection)
        """
        raise NotImplementedError

    @staticmethod
    def _check_values(data: list[Datum]) -> list[ErrorRecord]:
        """
        Runs checks on data and returns any warnings found.
        A DataRetrievalError will be raised if no values are returned.
        """
        warnings: list[ErrorRecord] = []
        found_any = False

        for datum in data:
            if not found_any and datum.value is not None:
                found_any = True
            else:
                warnings.append(ErrorRecord(
                    level=ErrorLevel.WARNING,
                    message='Record found with null value',
                    record=datum.as_json_dict()
                ))

        if not found_any:
            raise EmptyResultsError('No values returned.')

        return warnings

    @staticmethod
    def _datums_from_indicator_caches(
            cache_items: QuerySet['CachedIndicatorData'],
            time_part_lookup: dict[str, 'TimeAxis.TimePart']
    ) -> list['Datum']:
        variable_slugs: list[str] = []
        geog_global_geoids: list[str] = []
        for item in cache_items:
            variable_slugs.append(item.variable)
            geog_global_geoids.append(item.geog)

        variable_lookup = {v.slug: v for v in Variable.objects.filter(slug__in=variable_slugs)}
        geog_lookup = {g.global_geoid: g for g in AdminRegion.objects.filter(global_geoid__in=geog_global_geoids)}
        return [Datum(
            variable=variable_lookup[item.variable],
            geog=geog_lookup[item.geog],
            time=time_part_lookup[item.time_part_hash],
            value=item.value,
            moe=item.moe,
            denom=item.denom,
        ) for item in cache_items]

    def _generate_cache_key(self, geogs: QuerySet['AdminRegion'], time_axis: 'TimeAxis', use_denom=True,
                            agg_method=None, parent_geog_lvl: Optional[Type['AdminRegion']] = None):
        geog_key = tuple(sorted((geog.global_geoid for geog in geogs.all())))
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

    def _add_warning(self, warning: ErrorRecord):
        self._warnings += [warning]

    def _add_warnings(self, warnings: List[ErrorRecord]):
        self._warnings += warnings

    def __str__(self):
        return f'{self.name} ({self.slug})'


class CensusVariable(Variable):
    sources = models.ManyToManyField(
        'CensusSource',
        related_name='census_variables',
        through='CensusVariableSource'
    )

    _agg_methods = {
        AggregationMethod.NONE: None,
        AggregationMethod.COUNT: models.Count,
        AggregationMethod.SUM: models.Sum,
        AggregationMethod.MEAN: models.Avg,
        AggregationMethod.MODE: None,
        AggregationMethod.MAX: models.Max,
        AggregationMethod.MIN: models.Min,
    }

    @property
    def children(self) -> List[QuerySet]:
        return [self.sources.all()]

    class Meta:
        verbose_name = 'Census Variable'
        verbose_name_plural = 'Census Variables'

    def _get_values(self,
                    geog_collection: GeogCollection,
                    time_axis: TimeAxis,
                    use_denom=True,
                    agg_method=None) -> list[Datum]:
        """
        Goes across each geography in the collection and finds its subgeographies and then returns
        values, an aggregate of their subgeogs' values if necessary, for each geog in GeogCollection geogs

        :returns a flat list of Datums of length len(time_axis) * len(geog_collection)
        """
        # 2a. get values for full set of subgeogs
        results: list[Datum] = []
        geog_record: GeogRecord
        for geog_record in geog_collection.records.values():
            geog_record.data = []
            for subgeog in geog_record.subgeogs:
                geog_record.add_time_part_records(
                    subgeog,
                    self._get_values_for_geog(subgeog, time_axis, use_denom)
                )
            # 2b. aggregate those values up to the set of neighbor geogs
            # and add the Datums to the final flat list of results
            results += list(geog_record.get_aggregate_data(self, time_axis, use_denom).values())

        return results

    def _get_values_for_geog(self,
                             geog: AdminRegion,
                             time_axis: TimeAxis,
                             use_denom=True) -> dict[str, Datum]:
        """
        Retrieves data for the variable instance at the geography `geog_record.geog`
        :returns dict that maps time_part slugs to the data at that time
        """
        # get the census/acs tables for the points in time_axis
        census_table_records_by_year: Dict[
            str, QuerySet[CensusTableRecord]] = self.get_census_table_records_for_time_axis(time_axis)
        denom_census_table_records_by_year: Dict[str, QuerySet[CensusTableRecord]] = {}

        if use_denom:
            denoms = self.denominators.all()
            denom_census_table_records_by_year = denoms[0].get_census_table_records_for_time_axis(
                time_axis) if denoms else {}

        # extract and compute the values at each point in time_axis
        results: dict[str, Datum] = {}
        time_part_hash: str
        for time_part_hash, records in census_table_records_by_year.items():
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
                moe: Optional[float] = None
                # filter out null values
                all_moes = [result['moe'] for result in moe_results if result['moe'] is not None]
                if all_moes:
                    moe = math.sqrt(sum(all_moes))

            else:
                self._add_warning(
                    ErrorRecord(
                        level=ErrorLevel.WARNING,
                        message='Margins of Error for compound variables cannot be accurately reported at this time.'))
                moe = None

            # if denom is being used, look up the corresponding record and get its value
            denom, percent = None, None
            if use_denom and time_part_hash in denom_census_table_records_by_year:
                denom_record = denom_census_table_records_by_year[time_part_hash]
                denom_ids, _ = CensusTableRecord.get_table_uids(denom_record)
                denom = CensusValue.objects.filter(
                    geog_uid=geog.affgeoid,
                    census_table_uid__in=denom_ids
                ).values('geog_uid').annotate(denom=Sum('value')).values('denom')[0]['denom']
                if denom and denom > 0:
                    percent = val / denom

            results[time_part_hash] = Datum(variable=self, time=time_axis.time_part_lookup[time_part_hash], geog=geog,
                                            value=val, moe=moe, denom=denom, percent=percent)

        # return dict that maps time_part hashes to the data at that time
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
        data: dict[str, QuerySet['CensusTableRecord']] = {}
        for time_part in time_axis.time_parts:
            data[time_part.storage_hash] = self._get_census_table_record_for_time_part(time_part)
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
        AggregationMethod.NONE: None,
        AggregationMethod.COUNT: 'COUNT',
        AggregationMethod.SUM: 'SUM',
        AggregationMethod.MEAN: 'AVG',
        AggregationMethod.MODE: None,
        AggregationMethod.MAX: 'MAX',
        AggregationMethod.MIN: 'MIN',
    }

    @property
    def children(self) -> List[QuerySet]:
        return [self.sources.all()]

    class Meta:
        verbose_name = 'CKAN Variable'
        verbose_name_plural = 'CKAN Variables'

    def _get_values(self,
                    geog_collection: GeogCollection,
                    time_axis: TimeAxis,
                    use_denom=True,
                    agg_method=None) -> list[Datum]:
        """
        Goes across each geography in the collection and finds its subgeographies and then returns
        values, an aggregate of their subgeogs' values if necessary, for each geog in GeogCollection geogs

        :returns a flat list of Datums of length len(time_axis) * len(geog_collection)
        """
        results: list[Datum] = []
        parent_geog_lvl: Type['AdminRegion'] = geog_collection.geog_type
        sub_geogs: QuerySet['AdminRegion'] = geog_collection.all_subgeogs
        print('GETTING')
        for time_part in time_axis.time_parts:
            source: CKANSource = self._get_source_for_time_part(time_part)
            denom_select, denom_data = self._get_denom_data(source, sub_geogs, time_part) if use_denom else (None, None)

            # get the raw data for this geog and time_part from CKAN
            query = source.get_data_query(
                self,
                sub_geogs,
                time_part,
                parent_geog_lvl=parent_geog_lvl,
                denom_select=denom_select
            )

            # get data from ckan and wrap it in our Datum class
            raw_data: list[dict] = source.query_datastore(query)
            var_data: list[Datum] = Datum.from_ckan_response_data(self, raw_data, time_axis.time_part_lookup)

            # for regional sources, we need to aggregate here for now
            if parent_geog_lvl and type(source) == CKANRegionalSource:
                var_data = self._aggregate_data(var_data, type(sub_geogs[0]), parent_geog_lvl)
                if denom_data:
                    denom_data = self._aggregate_data(denom_data, type(sub_geogs[0]), parent_geog_lvl)

            if denom_data:
                # we need to link the data
                results += self._join_data(var_data, denom_data)
            else:
                # either no denom at all, or denom was in same source, and captured using `denom_select`
                results += var_data

        # at this point, results
        return results

    @property
    def agg_str(self):
        return '' if self.aggregation_method == AggregationMethod.NONE else self.aggregation_method

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
        parent_sq = Subquery(parent_geog_lvl.objects.filter(geom__covers=OuterRef('geom')).values('global_geoid'))

        # filter to geoids found in data
        lookup_geogs: QuerySet[AdminRegion] = base_geog_lvl.objects.filter(
            global_geoid__in=[d.geog.global_geoid for d in data]
        ).annotate(parent_global_geoid=parent_sq)

        # make lookup dict from queryset
        parent_geog_lookup = {geog.global_geoid: AdminRegion.objects.get(global_geoid=geog.parent_global_geoid) for geog
                              in lookup_geogs}

        # using lookup, replace each datum's geog with the parent one
        joined_data = [datum.update(geog=parent_geog_lookup[datum.geog.global_geoid]) for datum in data]

        # split data by parent_geog
        parent_data = {}
        for datum in joined_data:
            geog_key = datum.geog
            time_key = datum.time

            if geog_key not in parent_data:
                parent_data[geog_key] = {time_key: [datum]}

            else:
                if time_key in parent_data[geog_key]:
                    parent_data[geog_key][time_key] += [datum]
                else:
                    parent_data[geog_key][time_key] = [datum]

        results: list[Datum] = []
        parent_geog: 'AdminRegion'
        time_record: dict[TimeAxis.TimePart, list['Datum']]
        for parent_geog, time_record in parent_data.items():
            for time, data in time_record.items():
                values = [float(d.value) if d.value is not None else None for d in data]
                denoms = [d.denom for d in data]
                if len(data) == 1:
                    value = values[0]
                    denom = denoms[0]
                else:
                    if None in values:
                        raise AggregationError(
                            f"Cannot aggregate data for '{parent_geog.name}' since data is not available for all of "
                            f"its constituent '{base_geog_lvl.geog_type}'s.")
                    if None in denoms:
                        self._add_warning(ErrorRecord(
                            level=ErrorLevel.WARNING,
                            message=f"Cannot aggregate denominator data for '{parent_geog.name}' at '{time}' "
                                    f"since data is not available for "
                                    f"all of its constituent '{base_geog_lvl.geog_type_title}'s"))
                    value = self.aggregation_method_fn(values)
                    denom = self.aggregation_method_fn(denoms) if len(denoms) and None not in denoms else None

                results.append(Datum(variable=self, geog=parent_geog, time=time, value=value, denom=denom))
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
        time_part_lookup: dict[str, time_part] = {time_part.storage_hash: time_part}

        if denom_var:
            if len(denom_var.sources.filter(pk=source.pk)):
                # if denom uses the same source we can simply pass its field select
                denom_select = f'{denom_var.agg_str}("{denom_var.field}")'
            else:
                # if not, keep the denom select null , but fire off a call to collect
                denom_source = denom_var._get_source_for_time_part(time_part)
                denom_query = denom_source.get_data_query(denom_var, geogs, time_part)
                denom_data = Datum.from_ckan_response_data(
                    denom_var,
                    source.query_datastore(denom_query),
                    time_part_lookup
                )

        return denom_select, denom_data


class CensusVariableSource(models.Model):
    """ for linking Census variables to their sources while keeping track of the census formula format for that combo"""
    variable = models.ForeignKey('CensusVariable', on_delete=models.CASCADE, related_name='variable_to_source')
    source = models.ForeignKey('CensusSource', on_delete=models.CASCADE, related_name='source_to_variable')
    census_table_records = models.ManyToManyField('census_data.CensusTableRecord')

    class Meta:
        index_together = ('variable', 'source',)
        unique_together = ('variable', 'source',)
