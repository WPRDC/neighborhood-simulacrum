from dataclasses import dataclass
from typing import Union, TYPE_CHECKING, Type, Optional

from django.contrib.gis.db.models import Union as GeoUnion
from django.db import models
from django.db.models import QuerySet
from polymorphic.models import PolymorphicModel

from geo.models import CensusGeography, Tract, County, BlockGroup, CountySubdivision
from indicators.models.time import TimeAxis
from indicators.models.abstract import Described

if TYPE_CHECKING:
    from indicators.models import CKANVariable


class Source(PolymorphicModel, Described):
    """ Base class that defines data sources """
    time_coverage_start = models.DateTimeField()
    time_coverage_end = models.DateTimeField(help_text='Leave blank for indefinite', blank=True, null=True)

    time_granularity = models.IntegerField(help_text='Select the smallest unit of time this source can aggregate to',
                                           choices=TimeAxis.UNIT_CHOICES)

    @property
    def info_link(self):
        """ Link to external resource where user can find info on data source and/or the source itself."""
        raise NotImplementedError

    def can_handle_time_part(self, time_part: 'TimeAxis.TimePart') -> bool:
        raise NotImplementedError

    def can_handle_geography(self, geog: CensusGeography):
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

    @property
    def info_link(self):
        return 'https://www.census.gov/' if self.dataset == 'CEN' else 'https://www.census.gov/programs-surveys/acs/'

    def can_handle_time_part(self, time_part: 'TimeAxis.TimePart') -> bool:
        if time_part.time_unit == TimeAxis.YEAR:
            return self.time_coverage_start < time_part.time_point < self.time_coverage_end
        return False

    def can_handle_geography(self, geog: CensusGeography):
        # todo: update this when we add neighborhoods etc
        return True


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

    def clean(self):
        if not self.time_field:
            # todo: check that the unit covers the time coverage
            pass

    def can_handle_time_part(self, time_part: 'TimeAxis.TimePart') -> bool:
        if time_part.time_unit == TimeAxis.YEAR:
            return self.time_coverage_start <= time_part.time_point <= self.time_coverage_end
        return False

    def can_handle_geography(self, geog: CensusGeography):
        raise NotImplementedError

    def get_geog_filter_sql(self, geogs: QuerySet['CensusGeography']) -> str:
        """
        Returns chunk of SQL to go in the WHERE clause to filter the datasource to `geog`
        since the child models of CKANSource exist to handle different ways of representing geometry,
        this must be implemented in those models.
        """
        raise NotImplementedError

    def get_time_filter_sql(self, time_part: 'TimeAxis.TimePart', time_select: str):
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
        pass

    def get_subclass_instance(self):
        """
        Returns the object of the subclass for
        a particular object of this model.

        :return: (subclass of `Source` | None)
        """
        for attr in (
                'ckangeomsource',
                'ckanparcelsource',
                'ckanregionalsource'
        ):
            if hasattr(self, attr):
                return getattr(self, attr)
        return None

    def get_values_across_geo_sql(self, variable: 'CKANVariable', geog_type: Type['CensusGeography'], ) -> str:
        raise NotImplementedError

    def get_single_value_sql(self, variable: 'CKANVariable', geog: 'CensusGeography', ) -> str:
        raise NotImplementedError

        cast = '::float'
        aggr_mthd: str = variable.aggregation_method
        if variable.aggregation_method == variable.NONE:
            aggr_mthd = 'SUM'

        return f"""{aggr_mthd}(dt."{variable.field}"){cast}"""

    def _get_time_select_sql(self) -> str:
        return f'dt."{self.time_field or "date"}"'

    def _get_geog_select(self, geogs: QuerySet['CensusGeography']) -> str:
        raise NotImplementedError

    def _get_from_subquery(self, geog_type: Type[CensusGeography]) -> str:
        raise NotImplementedError

    def get_data_query(self, variable: 'CKANVariable', geogs: QuerySet['CensusGeography'],
                       time_part: 'TimeAxis.TimePart') -> str:
        # get fields from source to select
        geog_select = self._get_geog_select(geogs)
        time_select = self._get_time_select_sql()
        value_select = self._get_value_select_sql(variable)

        # get space and time filters
        geog_filter = self.get_geog_filter_sql(geogs)
        time_filter = self.get_time_filter_sql(time_part, time_select)

        from_subq = self._get_from_subquery()

        return f"""
        SELECT 
            {geog_select}       as __s_geog__, 
            {time_select}       as __s_time__,
            {value_select}      as __s_value__            
        FROM {from_subq} as dt
        WHERE {geog_filter} AND {time_filter}
        """


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

    def can_handle_geography(self, geog: CensusGeography):
        # while there may be no data in a geog, geocoded datasets can work with any geog
        return True

    def get_geog_filter_sql(self, geogs: QuerySet['CensusGeography']) -> str:
        """
        Returns a string of sql for use in where clause to filter results to those
        in the union of the geographies in `geogs`.

        :param geogs:
        :return:
        """
        geofence = geogs.aggregate(the_geom=GeoUnion('geom'))
        return f"""
        ST_Intersects(
            ST_GeomFromWKT('{geofence['geom'].wkt}')
            {self.geom_field}
        )"""

    def get_values_across_geo_sql(self, variable: 'CKANVariable', geog_type: Type['CensusGeography']) -> str:
        """ Generates SQL to send to CKAN to get data on variable across all geogs in geog_type for this source"""
        value_select = self._get_value_select_sql(variable)
        from_sql = self._get_from_subquery()
        # noinspection SqlResolve
        return f"""SELECT {value_select}, gt.id as geog_id
        FROM {from_sql} dt 
        JOIN "{geog_type.ckan_resource}" gt 
        ON ST_CoveredBy(dt."{self.geom_field}", ST_GeomFromWKB(decode(gt.geom, 'hex')))
        GROUP BY gt.id
        """

    def get_single_value_sql(self, variable: 'CKANVariable', geog: 'CensusGeography') -> str:
        """ Generates SQL to send to CKAN to get data on variable across all geogs in geog_type for this source"""
        value_select = self._get_value_select_sql(variable)
        from_sql = self._get_from_subquery()
        # noinspection SqlResolve
        return f"""SELECT {value_select}
        FROM {from_sql} dt 
        WHERE ST_CoveredBy(dt."{self.geom_field}", ST_GeomFromWKT('{geog.geom.wkt}'))
        """

    def _get_geog_select(self, geogs: QuerySet['CensusGeography']) -> str:
        """ """
        return f'"GEO".the_geom'

    def _get_ckan_geog_lookup(self, geog_type: Type['CensusGeography']) -> Optional[CKANLookupSource]:
        lookup_mapping = {
            County: self.CKANLookupSource(table="8a5fc9dc-5eb9-4fe3-b60a-0366ad9b813b"),
            CountySubdivision: self.CKANLookupSource(table="35c72b10-147e-4bf3-8678-ae6e83ad1de2"),
            Tract: self.CKANLookupSource(table='bb9a7972-981c-4026-8483-df8bdd1801c2'),
            BlockGroup: self.CKANLookupSource(table="b5f5480c-548d-46d8-b623-40a226d87517"),
        }
        return lookup_mapping[geog_type] if geog_type in lookup_mapping else None

    def _get_from_subquery(self, geog_type: Type[CensusGeography]) -> str:
        """ Returns source table joined with geography table to get geoids """
        if self.standardization_query:
            source_qry = f'({self.standardization_query.replace("", "")})'
        else:
            source_qry = f'"{self.resource_id}"'

        geog_table = self._get_ckan_geog_lookup(geog_type)
        return f'{source_qry} "SRC" '
        f'JOIN {geog_table} "GEO" ON ST_Covers({geog_table}.the_geom, {source_qry}.{self.geom_field})'


class CKANRegionalSource(CKANSource):
    blockgroup_field = models.CharField(max_length=100, null=True, blank=True)
    blockgroup_field_is_sql = models.BooleanField(default=False)

    tract_field = models.CharField(max_length=100, null=True, blank=True)
    tract_field_is_sql = models.BooleanField(default=False)

    countysubdivision_field = models.CharField(max_length=100, null=True, blank=True)
    countysubdivision_field_is_sql = models.BooleanField(default=False)

    place_field = models.CharField(max_length=100, null=True, blank=True)
    place_field_is_sql = models.BooleanField(default=False)

    schooldistrict_field = models.CharField(verbose_name='School District field', max_length=100, null=True, blank=True)
    schooldistrict_field_is_sql = models.BooleanField(default=False)

    zipcode_field = models.CharField(verbose_name='Zip code field', max_length=100, null=True, blank=True)
    zipcode_field_is_sql = models.BooleanField(default=False)

    neighborhood_field = models.CharField(max_length=100, null=True, blank=True)
    neighborhood_field_is_sql = models.BooleanField(default=False)

    def get_source_geog_field(self, geog: Type[CensusGeography]) -> object:
        field_for_geoid_field = f'{geog.geog_type}_field'.lower()
        return getattr(self, field_for_geoid_field)

    def get_is_sql(self, geog: Union[CensusGeography, Type[CensusGeography]]):
        field_for_is_sql = f'{geog.geog_type}_field_is_sql'.lower()
        return getattr(self, field_for_is_sql)

    def can_handle_geography(self, geog: Union[CensusGeography, Type[CensusGeography]]):
        return bool(self.get_geoid_field(geog))

    def get_geog_filter_sql(self, geogs: QuerySet['CensusGeography']) -> str:
        """
        Creates a chunk of SQL to be used in the WHERE clause that
        filters a dataset described by `source` to data within the
        geographies in `geogs`
        """
        # based on the geog's type, pick which field in the source we want
        source_geog_field = self.get_source_geog_field(geogs[0])
        source_geog_field = f'"{source_geog_field}"'  # add double quotes to ensure case sensitivity

        # get filter by geoid
        geoids = f"""({', '.join([f"'{geog.common_geoid}'" for geog in geogs.all()])})"""

        return f""" {source_geog_field} IN {geoids} """

    def get_geoid_field(self, geog: CensusGeography):
        return self.get_source_geog_field(geog)

    def get_values_across_geo_sql(self, variable: 'CKANVariable', geog_type: Type['CensusGeography'], ):
        """ Generates SQL to send to CKAN to get data on variable across all geogs in geog_type for this source"""
        value_select = self._get_value_select_sql(variable)
        from_sql = self._get_from_subquery()
        source_geog_field = self.get_source_geog_field(geog_type)
        # noinspection SqlResolve
        return f"""SELECT {value_select},  gt.id as geog_id
        FROM {from_sql} dt 
        JOIN "{geog_type.ckan_resource}" gt 
        ON "{source_geog_field}" = gt.geoid
        GROUP BY gt.id"""

    def get_single_value_sql(self, variable: 'CKANVariable', geog: 'CensusGeography'):
        value_select = self._get_value_select_sql(variable)
        from_sql = self._get_from_subquery()
        source_geog_field = self.get_source_geog_field(geog)
        # noinspection SqlResolve
        return f"""SELECT {value_select}
        FROM {from_sql} dt 
        WHERE "{source_geog_field}" = '{geog.geoid}'"""

    def _get_geog_select(self, geogs: QuerySet['CensusGeography']) -> str:
        # todo: this operates on the assumption that all the geogs are the same type,
        #   this will probably remain true, but it should be formalized somewhere
        field = self.get_source_geog_field(geogs[0].__class__)
        return f'"{field}"'

    def _get_from_subquery(self, *args) -> str:
        """ Return subquery for source of data. """
        return f'({self.standardization_query.replace("", "")})' if self.standardization_query else f'"{self.resource_id}"'
