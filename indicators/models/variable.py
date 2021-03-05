from dataclasses import dataclass
from functools import lru_cache
from typing import Union, List, Dict, Optional, Type

import requests
from datetime import MINYEAR, MAXYEAR

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import QuerySet, Sum, Value
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from geo.models import CensusGeography
from indicators.models.viz import DataViz
from indicators.models.time import TimeAxis
from indicators.models.source import CensusSource, CKANSource
from indicators.models.abstract import Described

from census_data.models import CensusValue, CensusTable, CensusTablePointer

CKAN_API_BASE_URL = 'https://data.wprdc.org/api/3/'
DATASTORE_SEARCH_SQL_ENDPOINT = 'action/datastore_search_sql'


class Variable(PolymorphicModel, Described):
    short_name = models.CharField(max_length=26, null=True, blank=True)

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
        return None

    def get_primary_value(self, geog: CensusGeography, time_part: TimeAxis.TimePart) -> any:
        raise NotImplemented

    def get_value_and_moe(self, geog: CensusGeography, time_part: TimeAxis.TimePart) -> dict:
        raise NotImplemented

    def get_table_row(self, data_viz: DataViz, geog: CensusGeography) -> Dict[str, Union[dict, None]]:
        raise NotImplemented

    def get_chart_record(self, data_viz: DataViz, geog_type: CensusGeography) -> Dict[str, any]:
        raise NotImplemented

    def get_layer_data(self, data_viz: DataViz, geog: Type[CensusGeography]) -> Dict[str, any]:
        raise NotImplemented

    def carto_join(self, geog: 'CensusGeography'):
        # create a SQL join statement for use in carto
        raise NotImplemented

    def _get_all_values_at_geog_and_time_part(self, geog: CensusGeography, time_part: TimeAxis.TimePart) -> dict:
        """
        Returns a dict that contains the values retrieved with this variable when examined
        in 'geog' around (`time_unit`) the point in time 'time_point'

        the keys 'v' and 'm' are value and margin of error respectively.
        all proportional calculations are keyed by their denominator's slug
        {
            series: {v: val, m: margin, d1: p1, d2: p2},
        }
        """
        return {**self.get_value_and_moe(geog, time_part),
                **self.get_proportional_data(geog, time_part)}

    def get_proportional_datum(self, geog: CensusGeography, time_part: TimeAxis.TimePart,
                               denom_variable: "Variable") -> Union[float, None]:
        """ Get or calculate comparison of variable to one of its denominators"""
        # todo: make a `get_value` method to cut out this MoE cruft
        val_and_moe = self.get_value_and_moe(geog, time_part)
        denom_val_and_moe = denom_variable.get_value_and_moe(geog, time_part)
        if val_and_moe['v'] is None or denom_val_and_moe['v'] in [None, 0]:
            return None
        else:
            return float(val_and_moe['v']) / float(denom_val_and_moe['v'])

    def get_proportional_data(self, geog: CensusGeography, time_part: TimeAxis.TimePart) -> dict:
        """ Get or calculate comparison of variable to its denominators """
        data = {}
        for denom_variable in self.denominators.all():
            data[denom_variable.slug] = self.get_proportional_datum(geog, time_part, denom_variable)

        return data

    def can_handle_time_part(self, time_part: TimeAxis.TimePart) -> bool:
        for source in self.sources.all():
            if source.can_handle_time_part(time_part):
                return True
        return False

    def can_handle_geography(self, geog: CensusGeography) -> bool:
        for source in self.sources.all():
            if source.can_handle_geography(geog):
                return True
        return False

    def __str__(self):
        return f'{self.name} ({self.slug})'


class CensusVariable(Variable):
    sources = models.ManyToManyField(
        'CensusSource',
        related_name='census_variables',
        through='CensusVariableSource'
    )

    # Value getters
    def get_primary_value(self, geog: CensusGeography, time_part: TimeAxis.TimePart) -> any:
        """  Gets the primary value """
        return self.get_value_and_moe(geog, time_part)['v']

    def get_value_and_moe(self, geog: CensusGeography, time_part: TimeAxis.TimePart) -> dict:
        """ Find and return the value and margin of error for the variable at a geography and series """
        value: Optional[float] = 0
        moe: Optional[float] = 0
        na_flag = False
        source = self._get_source_for_time_point(time_part.time_point)

        # get census tables for time_point
        # get census table pointers for this variable
        # fixme: this is fine on one-by-one basis, but when doing batch value gathering, this adds a lot of overhead
        #   we should try to use querysets the whole way down to the value getting
        pointers = source.source_to_variable.get(variable=self).census_table_pointers.all()
        for ct_pointer in pointers:
            v, m = ct_pointer.get_values_at_geog(geog)
            if value is None or v is None:
                value = None
            else:
                value += v
            if moe is None or m is None:
                moe = None
            else:
                moe += m

        return {'v': value, 'm': moe}

    def get_values_over_geog_type(self, geog_type: Type[CensusGeography], time_part: 'TimeAxis.TimePart') -> dict:
        geogs = geog_type.objects.all()
        # queryset of relevant census tables
        census_tables = self.get_census_tables_for_time_part(time_part)
        # get values for all geogs at time, group by geog and sum values
        qs = CensusValue.objects.filter(geography__common_geoid__in=geogs, census_table__in=census_tables).values(
            "geography__common_geoid").annotate(value=Sum('value'))
        return {g['geography__common_geoid']: g['value'] for g in qs.all()}

    # Data presentation formats
    def get_table_row(self, data_viz: DataViz, geog: CensusGeography) -> Dict[str, Union[dict, None]]:
        """
        Gets the data for a table row. Data is collected for each series (column) in `data_viz`.
            If denominators are provided, sub rows will also be provided.
        """
        row = {}
        for time_part in data_viz.time_axis.time_parts:
            values = self._get_all_values_at_geog_and_time_part(geog, time_part)
            if values is not None:
                row[time_part.slug] = values
        return row

    def get_chart_record(self, data_viz: DataViz, geog: CensusGeography) -> Dict[str, any]:
        """
        Gets the data for one record displayed in a chart.
            {name: variable.name, [series.name]: f(value, series) }
        """
        record: Dict[str, any] = {'name': self.name}
        for time_part in data_viz.time_axis.time_parts:
            value = self.get_primary_value(geog, time_part)
            if value is not None:
                record[time_part.slug] = value
        return record

    def get_layer_data(self, data_viz: DataViz, geog_type: Type[CensusGeography]) -> Dict[str, any]:
        time_part = data_viz.time_axis.time_parts[0]
        # get data {geoid -> value}
        data = self.get_values_over_geog_type(geog_type, time_part)
        return data

    # Utils
    def get_census_tables_for_time_part(self, time_part: 'TimeAxis.TimePart') -> QuerySet['CensusTable']:
        source = self._get_source_for_time_point(time_part.time_point)
        census_table_ptrs = source.source_to_variable.get(variable=self).census_table_pointers.all()
        return CensusTable.objects.filter(value_to_pointer__in=census_table_ptrs)

    def _get_source_for_time_point(self, time_point: timezone.datetime) -> 'CensusSource':
        is_decade = not time_point.year % 10
        if is_decade:
            return self.sources.filter(dataset='CEN')[0]
        return self.sources.filter(dataset='ACS5')[0]  # fixme to handle actual cases


class CensusVariableSource(models.Model):
    """ for linking Census variables to their sources while keeping track of the census formula format for that combo"""
    variable = models.ForeignKey('CensusVariable', on_delete=models.CASCADE, related_name='variable_to_source')
    source = models.ForeignKey('CensusSource', on_delete=models.CASCADE, related_name='source_to_variable')
    census_table_pointers = models.ManyToManyField('census_data.CensusTablePointer')


class CKANVariable(Variable):
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
    aggregation_method = models.CharField(
        max_length=5,
        choices=AGGR_CHOICES,
        default=COUNT,
    )

    sources = models.ManyToManyField(
        'CKANSource',
        related_name='ckan_variables',
    )
    field = models.CharField(
        help_text='field in source to aggregate',
        max_length=100
    )
    sql_filter = models.TextField(help_text='SQL clause that will be used to filter data.', null=True, blank=True)

    # Value getters
    @lru_cache
    def get_primary_value(self, geog: CensusGeography, time_part: TimeAxis.TimePart) -> any:
        return self.get_value_and_moe(geog, time_part)['v']

    @lru_cache
    def get_value_and_moe(self, geog: CensusGeography, time_part: TimeAxis.TimePart) -> dict:
        value = self._fetch_value_from_ckan(time_part, geog)
        return {'v': value, 'm': None}

    def get_values_over_geog_type(self, geog_type: Type[CensusGeography], time_part: TimeAxis.TimePart):
        records = self._fetch_values_from_ckan(time_part, geog_type)
        return records

    # Data presentation formats
    def get_table_row(self, data_viz: DataViz, geog: CensusGeography) -> Dict[str, Union[dict, None]]:
        """
        Gets the data for a table row. Data is collected for each series (column) in `data_viz`.
            If denominators are provided, sub rows will also be provided.
        """
        row = {}
        for time_part in data_viz.time_axis.time_parts:
            values = self._get_all_values_at_geog_and_time_part(geog, time_part)
            if values is not None:
                row[time_part.slug] = values
        return row

    def get_chart_record(self, data_viz: DataViz, geog: CensusGeography) -> Dict[str, any]:
        """
        Gets the data for one record displayed in a chart.
            {name: variable.name, [series.name]: f(value, series) }
        """
        record: Dict[str, any] = {'name': self.name}
        for time_part in data_viz.time_axis.time_parts:
            value = self.get_primary_value(geog, time_part)
            if value is not None:
                record[time_part.slug] = value
        return record

    def get_layer_data(self, data_viz: DataViz, geog_type: Type[CensusGeography]) -> Dict[str, any]:
        time_part = data_viz.time_axis.time_parts[0]
        data = self.get_values_over_geog_type(geog_type, time_part)
        return data

    # Utils
    def _get_source_for_time_point(self, time_point: timezone.datetime) -> CKANSource:
        """ Return CKAN source that covers the time in `time_point` """
        # fixme: we'll need to come up with a more correct way of doing this: maybe a `through` relationship
        source: CKANSource
        for source in self.sources.all():
            # go through the sources and get the first one who's range covers the point
            start = source.time_coverage_start if source.time_coverage_start else timezone.datetime(MINYEAR, 1, 1)
            end = source.time_coverage_end if source.time_coverage_end else timezone.datetime(MAXYEAR, 1, 1)
            if start < time_point < end:
                return source
        return self.sources.all()[0]  # hack cop-out for now to keep this functions type

    # TODO: make this a function and put it in utils or something
    @staticmethod
    def _query_datastore(query: str):
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
        return data

    def _fetch_value_from_ckan(self, time_part: TimeAxis.TimePart, geog: CensusGeography):
        """
        Query CKAN for some aggregation of this variable within its geography.
        (e.g. mean housing sale price in Bloomfield)
        """
        source = self._get_source_for_time_point(time_part.time_point)
        query = source.get_single_value_sql(self, geog)
        data = self._query_datastore(query)
        try:
            return data[0]['v']
        except (IndexError, KeyError,):
            # these cases involve data missing upstream (e.g. excluded geog for privacy, upstream human error)
            return None

    def _fetch_values_from_ckan(self, time_part: TimeAxis.TimePart, geog_type: Type[CensusGeography]):
        """
        Query CKAN for some aggregation of this variable across geographies
        (e.g. mean housing sale price for each neighborhood)
        """
        source = self._get_source_for_time_point(time_part.time_point)
        query = source.get_values_across_geo_sql(self, geog_type)
        data = self._query_datastore(query)
        return data
