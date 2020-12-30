from typing import List, Union

from census import Census

from django.conf import settings
from django.db import models
from polymorphic.models import PolymorphicModel

from geo.models import CensusGeography
from indicators.models import TimeAxis
from indicators.models.abstract import Described


class Source(PolymorphicModel, Described):
    """ Base class that defines data sources """
    time_coverage_start = models.DateTimeField()
    time_coverage_end = models.DateTimeField(help_text='Leave blank for indefinite', blank=True, null=True)

    time_granularity = models.IntegerField(help_text='Select the smallest unit of time this source can aggregate to',
                                           choices=TimeAxis.UNIT_CHOICES)

    def can_handle_time_part(self, time_part: TimeAxis.TimePart) -> bool:
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

    def can_handle_time_part(self, time_part: TimeAxis.TimePart) -> bool:
        if time_part.time_unit == TimeAxis.YEAR:
            return self.time_coverage_start < time_part.time_point < self.time_coverage_end
        return False

    def can_handle_geography(self, geog: CensusGeography):
        # todo: update this when we add neighborhoods etc
        return True

    def get_data(self, formula_parts: Union[List[str], str], region: CensusGeography) -> []:
        tables = [formula_parts] if type(formula_parts) is str else formula_parts
        getter = self._get_api_caller()
        print(tables, region.census_geo)
        return getter.get(tables, region.census_geo)

    def _get_api_caller(self):
        c = Census(settings.CENSUS_API_KEY)
        if self.dataset == 'ACS5':
            return c.acs5
        if self.dataset == 'CEN':
            return c.sf1


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

    def can_handle_time_part(self, time_part: TimeAxis.TimePart) -> bool:
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

    def get_time_filter_sql(self, time_part: TimeAxis.TimePart):
        """
        Creates a chunk of SQL that will go in the WHERE clause that filters the dataset described by `source` to
        only have data within specific time frame.

        Said SQL chunk will compare the source data's 'time' field truncated to `time_unit`
         against `time_point` truncated to `time_unit`

        https://www.postgresql.org/docs/8.4/functions-datetime.html#FUNCTIONS-DATETIME-TRUNC
        """

        return f"""
        "{self.TIME_FIELD_ID}" = {time_part.trunc_str})"
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

    @staticmethod
    def get_field_for_geoid_field_for_geog(geog: CensusGeography):
        return f'{geog.region_type}_field'.lower()

    def can_handle_geography(self, geog: CensusGeography):
        return bool(self.get_geoid_field(geog))

    def get_geom_filter_sql(self, geog: CensusGeography) -> str:
        """
        Creates a chunk of SQL to be used in the WHERE clause that
        filters a dataset described by `source` to data within the
        geography described by `region`
        """
        # based on the region's type, pick which field in the source we want
        field_for_geoid_field = self.get_field_for_geoid_field_for_geog(geog)
        source_region_field = getattr(self, field_for_geoid_field)
        is_sql = getattr(self, f'{field_for_geoid_field}_is_sql')

        if not is_sql:
            source_region_field = f'"{source_region_field}"'  # add double quotes to ensure case sensitivity

        return f""" {source_region_field} LIKE '{geog.geoid}' """

    def get_geoid_field(self, geog: CensusGeography):
        field_for_geoid_field = self.get_field_for_geoid_field_for_geog(geog)
        geoid_field = getattr(self, field_for_geoid_field, None)
        return geoid_field
