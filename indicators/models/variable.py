from typing import Union, List, Dict

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from polymorphic.models import PolymorphicModel

from geo.models import CensusGeography
from indicators.models.viz import DataViz
from indicators.models.series import Series
from indicators.models.source import CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource
from indicators.models.abstract import Described

CKAN_API_BASE_URL = 'https://data.wprdc.org/api/3/'
DATASTORE_SEARCH_SQL_ENDPOINT = 'action/datastore_search_sql'


class Variable(Described, PolymorphicModel):
    units = models.CharField(
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
    def percent_label(self):
        return self.percent_label_text if self.percent_label_text else f'% of {self.title}'


class CensusVariable(Variable):
    sources = models.ManyToManyField(
        'CensusSource',
        related_name='census_variables',
        through='CensusVariableSource'
    )  # todo: ensure that there are no overlapping series across sources

    @property
    def all_census_tables(self):
        return {
            self._get_source_for_series(series).slug: self._get_formula_parts_at_series(series)
            for series in Series.objects.filter(sources__in=self.sources.all())
        }

    def get_table_row(self, data_viz: DataViz, region: CensusGeography) -> Dict[str, Union[dict, None]]:
        """
        Gets the data for a table row. Data is collected for each series (column) in `data_viz`.
            If denominators are provided, sub rows will also be provided.
        """
        row = {}
        for series in data_viz.series.all():
            values = self._get_values_for_region_over_series(region, series)
            if values is not None:
                row[series.slug] = values
        return row

    def get_value_and_moe(self, region: CensusGeography, series: Series) -> dict:
        """ Find and return the value and margin of error for the variable at a region and series """
        value: float = 0
        moe: float = 0
        source = self._get_source_for_series(series)

        for part in self._get_formula_parts_at_series(series):
            census_value = self._get_or_create_census_value(part, region, source).value
            if part[-1] == 'M':
                moe += census_value if census_value > 0 else 0  # todo: handle census MOE special values
            else:
                value += census_value
        return {'v': value, 'm': moe}

    def _get_values_for_region_over_series(self, region: CensusGeography, series: Series) -> dict:
        """
        Returns a dict that contains the values retrieved with this variable when examined
        in 'region' across the series in 'series'

        the keys 'v' and 'm' are value and margin of error respectively.
        all proportional calculations are keyed by their denominator's slug
        {
            series: {v: val, m: margin, d1: p1, d2: p2},
        }
        """
        return {**self.get_value_and_moe(region, series), **self._get_proportional_data(region, series)}

    def _get_source_for_series(self, series: Series) -> CensusSource:
        return self.sources.get(series=series)

    def _get_formula_parts_at_series(self, series: Series) -> List[str]:
        return self._split_formula(self._get_formula_at_series(series), self._get_source_for_series(series))

    def _get_formula_at_series(self, series: Series) -> Union[str, None]:
        formula: Union[str, None] = None
        try:
            source: CensusSource = self._get_source_for_series(series)
            formula = source.source_to_variable.get(variable=self).formula
        finally:
            return formula

    def _fetch_data_for_region(self, formula_parts: List[str], region: CensusGeography, series: Series):
        source = self._get_source_for_series(series)

        return source.get_data(formula_parts, region)

    @staticmethod
    def _split_formula(formula: str, source: CensusSource) -> List[str]:
        """
        Splits up the formula into a list of its table_ids
            for datasets with margins of error, it creates and adds the value and moe table_ids to the list
        """
        result = []
        for part in formula.split('+'):
            if source.dataset == 'CEN':
                result.append(part)
            else:
                result.append(part + 'E')
                result.append(part + 'M')
        return result

    def _get_proportional_datum(
            self,
            region: CensusGeography,
            series: Series,
            denom_variable: Variable) -> Union[float, None]:
        """ Get or calculate comparison of variable to one of its denominators"""
        # todo: make a `get_value` method to cut out this MoE cruft
        val_and_moe = self.get_value_and_moe(region, series)
        denom_val_and_moe = denom_variable.get_value_and_moe(region, series)
        if val_and_moe['v'] is None or denom_val_and_moe['v'] in [None, 0]:
            return None
        else:
            return 100 * val_and_moe['v'] / denom_val_and_moe['v']

    def _get_proportional_data(self, region: CensusGeography, series: Series) -> dict:
        """ Get or calculate comparison of variable to its denominators """
        data = {}
        for denom_variable in self.denominators.all():
            data[denom_variable.slug] = self._get_proportional_datum(region, series, denom_variable)

        return data

    def _extract_values_from_api_response(self, region: CensusGeography, series: Series, response_data: dict) -> None:
        """
        Take response data and store it into a CensusValue object that is linked to this variable
            and the region provided to the method.
        """
        for part in self.formula_parts:
            if not CensusValue.objects.filter(census_table=part, region=region):
                cv = CensusValue(census_table=part, region=region, value=response_data[self.source][0][part])
                cv.save()

    @staticmethod
    def _get_or_create_census_value(table: str, region: CensusGeography, source: CensusSource):
        try:
            return CensusValue.objects.filter(census_table=table, region=region)[0]  # fixme: should be get
        except (ObjectDoesNotExist, IndexError):
            value: float = source.get_data(table, region)[0][table]
            cv = CensusValue(census_table=table, region=region, value=value)
            cv.save()
            return cv

    def __str__(self):
        return f'{self.slug}'


class CensusVariableSource(models.Model):
    """ for linking Census variables to their sources while keeping track of the census formula format for that combo"""
    variable = models.ForeignKey('CensusVariable', on_delete=models.CASCADE, related_name='variable_to_source')
    source = models.ForeignKey('CensusSource', on_delete=models.CASCADE, related_name='source_to_variable')
    formula = models.TextField()


class CensusValue(models.Model):
    """
    stores a single (region, table, value) tuple
    the the values stored here are a function of the Variable, the Series, and the Geography
    the census table is unique to a Variable-Series combination and is where they're effect comes in
    """
    region = models.ForeignKey('geo.Geography', on_delete=models.CASCADE, db_index=True)
    census_table = models.CharField(max_length=15, db_index=True)  # the census table is a function of the series
    value = models.FloatField(null=True, blank=True)

    class Meta:
        index_together = ('region', 'census_table',)
        unique_together = ('region', 'census_table',)

    def __str__(self):
        return f'{self.census_table}/{self.region} ({self.value})'


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

    sources = models.ManyToManyField(
        'CKANSource',
        related_name='ckan_variables',
    )

    aggregation_method = models.CharField(
        max_length=5,
        choices=AGGR_CHOICES,
        default=COUNT,
    )

    field = models.CharField(
        help_text='field in source to aggregate',
        max_length=100
    )
    sql_filter = models.TextField(help_text='SQL clause that will be used to filter data.', null=True, blank=True)

    def get_table_row(self, data_viz: DataViz, region: CensusGeography) -> Dict[str, Union[dict, None]]:
        """
        Gets the data for a table row. Data is collected for each series (column) in `data_viz`.
            If denominators are provided, sub rows will also be provided.
        """
        row = {}
        for series in data_viz.series.all():
            values = self._get_values_for_region_over_series(region, series)
            if values is not None:
                row[series.slug] = values
        return row

    def get_value_and_moe(self, region: CensusGeography, series: Series) -> dict:
        value: float = 0
        source = self._get_source_for_series(series)
        value = self.aggregate_variable_at_region(series, region);
        return {'v': value, 'm': None}

    def _get_values_for_region_over_series(self, region: CensusGeography, series: Series) -> dict:
        """
        Returns a dict that contains the values retrieved with this variable when examined
        in 'region' across the series in 'series'

        the keys 'v' and 'm' are value and margin of error respectively.
        all proportional calculations are keyed by their denominator's slug
        {
            series: {v: val, m: margin, d1: p1, d2: p2},
        }
        """
        return self.get_value_and_moe(region, series)

    def _get_source_for_series(self, series: Series) -> CensusSource:
        return self.sources.get(series=series)

    def _query_datastore(self, query: str):
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
        value = data[0]['value']
        return value

    def _generate_intersect_clause(self, source: CKANGeomSource, region: CensusGeography) -> str:
        return f"""
        ST_Intersects(
            ST_GeomFromText('{region.geom.wkt}', {region.geom.srid}),
            {source.geom_field}
        )"""

    def _generate_region_name_filter_clause(self, source: CKANRegionalSource, region: CensusGeography) -> str:
        """
        Creates a chunk of SQL to be used in the WHERE clause that
        filters a dataset described by `source` to data within the
        geography described by `region`
        """
        # based on the region's type, pick which field in the source we want
        field_type = f'{region.TYPE}_field'
        source_region_field = getattr(source, field_type)
        return f"""
        "{source_region_field}" LIKE '{region.geoid}'
        """

    def aggregate_variable_at_region(self, series: Series, region: CensusGeography):
        """
        Query CKAN for aggregation of variable within it's region.
        (e.g. mean housing sale price in Bloomfield)
        """
        geo_filter_clause = ''
        join_statement = ''

        source = self._get_source_for_series(series)

        target_field = self.field if self.field in (
            '*',) else f'"{self.field}"'
        resource_id = source.resource_id
        aggregation_method = self.aggregation_method if self.aggregation_method != 'NONE' else ''

        cast = '::int' if aggregation_method in ('COUNT',) else ''

        if type(source) == CKANGeomSource:
            geo_filter_clause = self._generate_intersect_clause(source, region)
        elif type(source) == CKANRegionalSource:
            geo_filter_clause = self._generate_region_name_filter_clause(source, region)

        # generate sql query to send to `/datastore_search_sql` endpoint
        query = f"""
        SELECT {aggregation_method}({target_field}){cast} as value
        FROM {f'({join_statement}) as sub_query' if join_statement else f'"{resource_id}"'}
        WHERE  {f'{self.sql_filter} AND' if self.sql_filter else ''}
            {geo_filter_clause}
        """
        return self._query_datastore(query)
