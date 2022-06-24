import datetime
import logging
from dataclasses import dataclass
from typing import Union, Type, Optional, TYPE_CHECKING

import psycopg2
from django.contrib.gis.db.models import Union as GeoUnion
from django.db import models
from django.db.models import QuerySet
from polymorphic.models import PolymorphicModel
from psycopg2.extras import RealDictCursor, RealDictConnection

from context.models import WithTags, WithContext
from geo.models import AdminRegion, Tract, County, BlockGroup, CountySubdivision, SchoolDistrict
from indicators.models.time import TimeAxis
from profiles.abstract_models import Described
from profiles.local_settings import DATASTORE_NAME, DATASTORE_HOST, DATASTORE_USER, DATASTORE_PASSWORD, DATASTORE_PORT
from profiles.settings import SQ_ALIAS, GEO_ALIAS, DENOM_DKEY

logger = logging.getLogger(__name__)

datastore_settings = {
    'host': DATASTORE_HOST,
    'port': DATASTORE_PORT,
    'dbname': DATASTORE_NAME,
    'user': DATASTORE_USER,
    'password': DATASTORE_PASSWORD,
}

if TYPE_CHECKING:
    from indicators.models.variable import CKANVariable


class Source(PolymorphicModel, Described, WithTags, WithContext):
    """ Base class that defines data sources """
    time_coverage_start = models.DateTimeField()
    time_coverage_end = models.DateTimeField(
        help_text='Leave blank for indefinite',
        blank=True,
        null=True
    )

    time_granularity = models.IntegerField(
        help_text='Select the smallest unit of time this source can aggregate to',
        choices=TimeAxis.UNIT_CHOICES
    )

    @property
    def info_link(self):
        """ Link to external resource where user can find info on data source and/or the source itself."""
        raise NotImplementedError

    @property
    def static_date(self) -> Optional[str]:
        time_dict = {'year': 0, 'month': 1, 'day': 1, 'hour': 0, 'minute': 0}
        for i in range(TimeAxis.YEAR, self.time_granularity - 1, -1):
            unit = TimeAxis.UNIT_FIELDS[i]  # eg 'year'
            time_dict[unit] = self.time_coverage_start.__getattribute__(unit)
        return datetime.datetime(**time_dict).isoformat(sep=' ')

    def can_handle_time_part(self, time_part: 'TimeAxis.TimePart') -> bool:
        raise NotImplementedError

    def can_handle_geography(self, geog: AdminRegion):
        raise NotImplementedError


class CensusSource(Source):
    DATASET_CHOICES = (
        ('CEN', 'Decennial Census'),
        ('ACS5', 'ACS 5-year'),
        ('ACS1', 'ACS 1-year'),
    )
    dataset = models.CharField(
        max_length=4,
        choices=DATASET_CHOICES,
        default='CEN'
    )

    class Meta:
        verbose_name = 'Census/ACS Source'
        verbose_name_plural = 'Census/ACS Sources'

    @property
    def info_link(self):
        return 'https://www.census.gov/' if self.dataset == 'CEN' else 'https://www.census.gov/programs-surveys/acs/'

    def can_handle_time_part(self, time_part: 'TimeAxis.TimePart') -> bool:
        if time_part.time_unit == TimeAxis.YEAR:
            return self.time_coverage_start < time_part.time_point < self.time_coverage_end
        return False

    def can_handle_geography(self, geog: AdminRegion):
        if type(geog) in (Tract, County, BlockGroup, SchoolDistrict, CountySubdivision):
            return True
        return False


class CKANSource(Source, PolymorphicModel):
    TIME_FIELD_ID = 'date'

    package_id = models.UUIDField()
    resource_id = models.UUIDField()

    time_field = models.CharField(
        help_text="Must be provided unless time coverage fits within 1 unit. "
                  "i.e. this source only covers one unit of time (e.g. a 2042 dog census)",
        max_length=255,
        blank=True, null=True)
    time_field_format = models.CharField(
        max_length=255,
        blank=True, null=True)

    standardization_query = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'CKAN Source'
        verbose_name_plural = 'CKAN Sources'

    @property
    def info_link(self):
        return f'https://data.wprdc.org/dataset/{self.package_id}'

    @property
    def std_time_sql_identifier(self):
        """ casts time field if necessary and assigns it a standard name """
        if self.time_field_format:
            return f""" to_timestamp("{self.time_field}",'{self.time_field_format}') as {self.TIME_FIELD_ID} """
        if self.time_field:
            return f""" "{self.time_field}" as {self.TIME_FIELD_ID} """
        return ""

    def can_handle_time_part(self, time_part: 'TimeAxis.TimePart') -> bool:
        if time_part.time_unit == TimeAxis.YEAR:
            return self.time_coverage_start <= time_part.time_point <= self.time_coverage_end
        return False

    def can_handle_geography(self, geog: AdminRegion):
        raise NotImplementedError

    def get_data_query(self, variable: 'CKANVariable', geogs: QuerySet['AdminRegion'],
                       time_part: 'TimeAxis.TimePart', denom_select: str = None,
                       parent_geog_lvl: Optional[Type[AdminRegion]] = None) -> str:

        # get fields from source to select
        geog_select = self._get_geog_select(geogs, parent_geog_lvl)
        time_select = self._get_time_select_sql()
        value_select = f'{SQ_ALIAS}."{variable.field}"'
        agg_str = variable.agg_str

        # get space and time filteget_data_queryrs
        geog_filter = self._get_geog_filter_sql(geogs)
        time_filter = self._get_time_filter_sql(time_part, time_select)

        geog_type = geogs.all()[0].__class__
        from_subq = self._get_from_subquery(geog_type, parent_geog_lvl=parent_geog_lvl)

        denom_select_and_alias = f', {denom_select} as {DENOM_DKEY}' if denom_select else ''

        query = f"""
        SELECT 
            {geog_select}                   as __geog__, 
            '{time_part.slug}'              as __time__,
            {agg_str}({value_select})       as __value__
            {denom_select_and_alias}
        FROM {from_subq} AS {SQ_ALIAS}
        WHERE {geog_filter} AND {time_filter} 
        """
        query += f"GROUP BY __geog__ " if agg_str else ''
        return query

    def clean(self):
        if not self.time_field:
            # todo: check that the unit covers the time coverage
            pass

    @staticmethod
    def query_datastore(query: str):
        conn: RealDictConnection = psycopg2.connect(**datastore_settings, cursor_factory=RealDictCursor)
        cur: RealDictCursor = conn.cursor()
        cur.execute(query)
        return cur.fetchall()

    # SQL Generators
    def _get_geog_filter_sql(self, geogs: QuerySet['AdminRegion']) -> str:
        """
        Returns chunk of SQL to go in the WHERE clause to filter the datasource to `geog`
        since the child models of CKANSource exist to handle different ways of representing geometry,
        this must be implemented in those models.
        """
        raise NotImplementedError

    def _get_time_filter_sql(self, time_part: 'TimeAxis.TimePart', time_select: str):
        """
        Creates a chunk of SQL that will go in the WHERE clause that filters the dataset described by `source` to
        only have data within specific time frame.

        Said SQL chunk will compare the source data's 'time' field truncated to `time_unit`
         against `time_point` truncated to `time_unit`

        https://www.postgresql.org/docs/8.4/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC
        """
        time_unit = time_part.unit_str

        return f"""
        date_trunc('{time_unit}',{time_select}::timestamp) = {time_part.trunc_sql_str}
        """

    def _get_time_select_sql(self) -> str:
        """ Returns the source's time field, or a string representing the sole time unit covered by the source"""
        return f'{SQ_ALIAS}."{self.time_field}"' if self.time_field else f"'{self.static_date}'"

    def _get_geog_select(self, geogs: QuerySet['AdminRegion'],
                         parent_lvl_geog: Optional[Type[AdminRegion]]) -> str:
        raise NotImplementedError

    def _get_from_subquery(self, geog_type: Type[AdminRegion],
                           parent_geog_lvl: Optional[Type[AdminRegion]] = None) -> str:
        raise NotImplementedError


class CKANGeomSource(CKANSource):
    @dataclass
    class CKANLookupSource(object):
        table: str
        geoid_field: str = 'geoid'
        geom_field: str = 'geom'

    DEFAULT_GEOM_FIELD = '_geom'

    geom_field = models.CharField(
        max_length=100,
        default=DEFAULT_GEOM_FIELD,
        null=True,
        blank=True
    )

    def can_handle_geography(self, geog: AdminRegion):
        # while there may be no data in a geog, geocoded datasets can work with any geog
        return True

    def _get_ckan_geog_lookup(self, geog_type: Type['AdminRegion']) -> Optional[CKANLookupSource]:
        """
        Returns the resource ID for the appropriate lookup table in CKAN.

        The lookup table has a columns for the geoid and geom (current hex string of its WKB).

        Using these allows us to reference geospatial data in SQL without having to send the geom;
        instead we can reference it through its geoid in the lookup table.
        """
        # todo: move this to settings
        lookup_mapping = {
            County: self.CKANLookupSource(table="8a5fc9dc-5eb9-4fe3-b60a-0366ad9b813b"),
            CountySubdivision: self.CKANLookupSource(table="35c72b10-147e-4bf3-8678-ae6e83ad1de2"),
            Tract: self.CKANLookupSource(table='bb9a7972-981c-4026-8483-df8bdd1801c2'),
            BlockGroup: self.CKANLookupSource(table="b5f5480c-548d-46d8-b623-40a226d87517"),
        }
        return lookup_mapping[geog_type] if geog_type in lookup_mapping else None

    # SQL Generators
    def _get_geog_filter_sql(self, geogs: QuerySet['AdminRegion']) -> str:
        """
        Returns a string of sql for use in `WHERE` clause to filter results to those within
        the boundary of the union of the geographies in `geogs`.

        :param geogs:
        :return:
        """
        geofence = geogs.aggregate(the_geom=GeoUnion('geom'))
        return f"""
        ST_Intersects(
            ST_GeomFromWKT('{geofence['geom'].wkt}')
            {self.geom_field}
        )"""

    def _get_geog_select(self, geogs: QuerySet['AdminRegion'],
                         parent_lvl_geog: Optional[Type[AdminRegion]]) -> str:
        if parent_lvl_geog:
            parent_table = f'"{parent_lvl_geog.ckan_resource}"'

            return f"SELECT geoid " \
                   f"FROM {parent_table} pt " \
                   f"WHERE ST_Covers(ST_GeomFromWKB(decode(pt.geom, 'hex')), {GEO_ALIAS}.the_geom)"

        # otherwise, return the geoid in the JOIN witht eh source sub query
        return f'{GEO_ALIAS}.geoid'

    def _get_from_subquery(self, geog_type: Type[AdminRegion], parent_geog_lvl=None) -> str:
        """
        Returns source table joined with geography table to get geoids.

        :param parent_geog_lvl:
        """
        if self.standardization_query:
            source_qry = f'({self.standardization_query.replace("", "")})'
        else:
            source_qry = f'"{self.resource_id}"'

        geog_table = self._get_ckan_geog_lookup(parent_geog_lvl or geog_type)
        return f'{source_qry} "SRC" ' \
               f'JOIN {geog_table} {GEO_ALIAS} ' \
               f'ON ST_Covers(ST_GeomFromWKB(decode({GEO_ALIAS}.geom, \'hex\')), "SRC".{self.geom_field})'


class CKANRegionalSource(CKANSource):
    blockgroup_field = models.CharField(max_length=100, null=True, blank=True)
    blockgroup_field_is_sql = models.BooleanField(default=False)

    tract_field = models.CharField(max_length=100, null=True, blank=True)
    tract_field_is_sql = models.BooleanField(default=False)

    countysubdivision_field = models.CharField(max_length=100, null=True, blank=True)
    countysubdivision_field_is_sql = models.BooleanField(default=False)

    county_field = models.CharField(max_length=100, null=True, blank=True)
    county_field_is_sql = models.BooleanField(default=False)

    place_field = models.CharField(max_length=100, null=True, blank=True)
    place_field_is_sql = models.BooleanField(default=False)

    schooldistrict_field = models.CharField(verbose_name='School District field', max_length=100, null=True, blank=True)
    schooldistrict_field_is_sql = models.BooleanField(default=False)

    zipcode_field = models.CharField(verbose_name='Zip code field', max_length=100, null=True, blank=True)
    zipcode_field_is_sql = models.BooleanField(default=False)

    neighborhood_field = models.CharField(max_length=100, null=True, blank=True)
    neighborhood_field_is_sql = models.BooleanField(default=False)

    def can_handle_geography(self, geog: Union[AdminRegion, Type[AdminRegion]]):
        return bool(self._get_source_geog_field(geog))

    def _get_source_geog_field(self, geog: Union[AdminRegion, Type[AdminRegion]]) -> object:
        field_for_geoid_field = f'{geog.geog_type_id}_field'.lower()
        return getattr(self, field_for_geoid_field)

    # SQL Generators
    def _get_geog_filter_sql(self, geogs: QuerySet['AdminRegion']) -> str:
        """
        Creates a chunk of SQL to be used in the WHERE clause that
        filters a dataset described by `source` to data within the
        geographies in `geogs`
        """
        # based on the geog's type, pick which field in the source we want
        source_geog_field = self._get_source_geog_field(geogs[0])
        source_geog_field = f'"{source_geog_field}"'  # add double quotes to ensure case sensitivity

        # get filter by geoid
        geoids = f"""({', '.join([f"'{geog.global_geoid}'" for geog in geogs.all()])})"""

        return f""" {source_geog_field} IN {geoids} """

    def _get_geog_select(self, geogs: QuerySet['AdminRegion'],
                         parent_lvl_geog: Optional[Type[AdminRegion]]) -> str:
        # regional sources need to be aggregated outside CKAN for now
        if parent_lvl_geog:
            print('parent_lvl_geog is ignored in CKANRegionalSources for now.')
        field = self._get_source_geog_field(geogs[0].__class__)
        return f'{SQ_ALIAS}."{field}"'

    def _get_from_subquery(self, geog_type, parent_geog_lvl=None) -> str:
        """
        Return subquery for source of data.
        :param parent_geog_lvl:
        """
        # join table or standardization query with the parent geog table on
        if self.standardization_query:
            return f'({self.standardization_query.replace("", "")})'
        return f'"{self.resource_id}"'
