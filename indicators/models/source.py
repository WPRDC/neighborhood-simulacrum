from typing import List, Union, TYPE_CHECKING, Type

from census import Census

from django.conf import settings
from django.db import models
from polymorphic.models import PolymorphicModel
from indicators.models import TimeAxis
from geo.models import CensusGeography
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
    TIME_FIELD_ID = '__the_time'

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

    def get_geom_filter_sql(self, region: CensusGeography) -> str:
        """
        Returns chunk of SQL to go in the WHERE clause to filter the datasource to `region`
        since the child models of CKANSource exist to handle different ways of representing geometry,
        this must be implemented in those models.
        """
        raise NotImplementedError

    def get_time_filter_sql(self, time_part: 'TimeAxis.TimePart'):
        """
        Creates a chunk of SQL that will go in the WHERE clause that filters the dataset described by `source` to
        only have data within specific time frame.

        Said SQL chunk will compare the source data's 'time' field truncated to `time_unit`
         against `time_point` truncated to `time_unit`

        https://www.postgresql.org/docs/8.4/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC
        """

        return f"""
        "{self.TIME_FIELD_ID}" = {time_part.trunc_sql_str})"
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


class CKANGeomSource(CKANSource):
    DEFAULT_GEOM_FIELD = '_geom'

    geom_field = models.CharField(
        max_length=100,
        default=DEFAULT_GEOM_FIELD,
        null=True,
        blank=True
    )

    def can_handle_geography(self, geog: CensusGeography):
        # while there may be no data in a region, geocoded datasets can work with any region
        return True

    def get_geom_filter_sql(self, region: CensusGeography) -> str:
        return f"""
        ST_Intersects(
            ST_GeomFromText('{region.geom.wkt}', {region.geom.srid}),
            {self.geom_field}
        )"""

    def get_values_across_geo_sql(self, variable: 'CKANVariable', geog_type: Type['CensusGeography']) -> str:
        """ Generates SQL to send to CKAN to get data on variable across all geogs in geog_type for this source"""
        cast = '::int' if variable.aggregation_method in ('COUNT',) else ''

        # noinspection SqlResolve
        return f"""SELECT {variable.aggregation_method}(dt."{variable.field}"){cast} as v,  gt.id as geog_id
        FROM "{self.resource_id}" dt 
        JOIN "{geog_type.ckan_resource}" gt 
        ON ST_CoveredBy(dt."{self.geom_field}", ST_GeomFromWKB(decode(gt.geom, 'hex')))
        GROUP BY gt.id
        """

    def get_single_value_sql(self, variable: 'CKANVariable', geog: 'CensusGeography') -> str:
        """ Generates SQL to send to CKAN to get data on variable across all geogs in geog_type for this source"""
        cast = '::int' if variable.aggregation_method in ('COUNT',) else ''

        # noinspection SqlResolve
        return f"""SELECT {variable.aggregation_method}(dt."{variable.field}"){cast} as v
        FROM "{self.resource_id}" dt 
        WHERE ST_CoveredBy(dt."{self.geom_field}", ST_GeomFromWKT('{geog.geom.wkt}'))
        """


class CKANRegionalSource(CKANSource):
    blockgroup_field = models.CharField(max_length=100, null=True, blank=True)
    blockgroup_field_is_sql = models.BooleanField(default=False)

    tract_field = models.CharField(max_length=100, null=True, blank=True)
    tract_field_is_sql = models.BooleanField(default=False)

    countysubdivision_field = models.CharField(max_length=100, null=True, blank=True)
    countysubdivision_field_is_sql = models.BooleanField(default=False)

    place_field = models.CharField(max_length=100, null=True, blank=True)
    place_field_is_sql = models.BooleanField(default=False)

    neighborhood_field = models.CharField(max_length=100, null=True, blank=True)
    neighborhood_field_is_sql = models.BooleanField(default=False)

    def get_source_geog_field(self, geog: Union[CensusGeography, Type[CensusGeography]]) -> object:
        field_for_geoid_field = f'{geog.region_type}_field'.lower()
        return getattr(self, field_for_geoid_field)

    def get_is_sql(self, geog: Union[CensusGeography, Type[CensusGeography]]):
        field_for_is_sql = f'{geog.region_type}_field_is_sql'.lower()
        return getattr(self, field_for_is_sql)

    def can_handle_geography(self, geog: Union[CensusGeography, Type[CensusGeography]]):
        return bool(self.get_geoid_field(geog))

    def get_geom_filter_sql(self, geog: CensusGeography) -> str:
        """
        Creates a chunk of SQL to be used in the WHERE clause that
        filters a dataset described by `source` to data within the
        geography described by `region`
        """
        # based on the region's type, pick which field in the source we want
        source_region_field = self.get_source_geog_field(geog)
        is_sql = self.get_is_sql(geog)

        if not is_sql:
            source_region_field = f'"{source_region_field}"'  # add double quotes to ensure case sensitivity

        return f""" {source_region_field} LIKE '{geog.geoid}' """

    def get_geoid_field(self, geog: CensusGeography):
        return self.get_source_geog_field(geog)

    def get_values_across_geo_sql(self, variable: 'CKANVariable', geog_type: Type['CensusGeography'], ):
        """ Generates SQL to send to CKAN to get data on variable across all geogs in geog_type for this source"""
        cast = '::int' if variable.aggregation_method in ('COUNT',) else ''
        source_geog_field = self.get_source_geog_field(geog_type)

        # noinspection SqlResolve
        return f"""SELECT {variable.aggregation_method}(dt."{variable.field}"){cast} as v,  gt.id as geog_id
        FROM "{self.resource_id}" dt 
        JOIN "{geog_type.ckan_resource}" gt 
        ON "{source_geog_field}" = gt.geoid
        GROUP BY gt.id"""

    def get_single_value_sql(self, variable: 'CKANVariable', geog: 'CensusGeography'):
        cast = '::int' if variable.aggregation_method in ('COUNT',) else ''
        source_geog_field = self.get_source_geog_field(type(geog))

        # noinspection SqlResolve
        return f"""SELECT {variable.aggregation_method}(dt."{variable.field}"){cast} as v
        FROM "{self.resource_id}" dt 
        WHERE "{source_geog_field}" = {geog.geoid}"""


# parcel
# noinspection SqlResolve
"""
SELECT sq.field, gt.geog_field as __geog
FROM (SELECT dt.field as field, pt.geom as parcel_geom
FROM table_id dt JOIN parcel_table pt ON dt.parid = pt.parid
) sq JOIN geog_table gt on st_coveredby(sq.parcel_geom, gt.geom)
"""
