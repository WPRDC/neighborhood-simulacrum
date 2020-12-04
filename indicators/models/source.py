from typing import List, Union

from census import Census

from django.conf import settings
from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from geo.models import CensusGeography
from indicators.models import TimeAxis
from indicators.models.abstract import Described


class Source(PolymorphicModel, Described):
    """ Base class that defines data sources """
    pass


class CensusSource(Source):
    # todo: make a model for these choices so we don't have to update code to add another census dataset
    #   unless there are some weird implementation details for a certain year that can't be easily parameterized
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

    def get_data(self, formula_parts: Union[List[str], str], region: CensusGeography) -> []:
        tables = [formula_parts] if type(formula_parts) is str else formula_parts
        getter = self._get_api_caller()
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

    time_coverage_start = models.DateTimeField(blank=True, null=True)
    time_coverage_end = models.DateTimeField(blank=True, null=True)

    time_field = models.CharField(max_length=255)
    time_field_format = models.CharField(
        max_length=255,
        blank=True, null=True)

    @property
    def std_time_sql_identifier(self):
        """ casts time field if necessary and assigns it a standard name """
        if self.time_field_format:
            return f""" to_timestamp("{self.time_field}",'{self.time_field_format}') as {self.TIME_FIELD_ID} """
        return f""" "{self.time_field}" as {self.TIME_FIELD_ID} """

    def get_geom_filter_sql(self, region: CensusGeography) -> str:
        """
        Returns chunk of SQL to go in the WHERE clause to filter the datasource to `region`
        since the child models of CKANSource exist to handle different ways of representing geometry,
        this must be implemented in those models.
        """
        return ''

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

    def get_geo_filter_sql(self, region: CensusGeography) -> str:
        return f"""
        ST_Intersects(
            ST_GeomFromText('{region.geom.wkt}', {region.geom.srid}),
            {self.geom_field}
        )"""


class CKANRegionalSource(CKANSource):
    blockgroup_field = models.CharField(max_length=100, null=True, blank=True)
    tract_field = models.CharField(max_length=100, null=True, blank=True)
    countysubdivision_field = models.CharField(max_length=100, null=True, blank=True)
    place_field = models.CharField(max_length=100, null=True, blank=True)
    neighborhood_field = models.CharField(max_length=100, null=True, blank=True)

    def get_geo_filter_sql(self, region: CensusGeography) -> str:
        """
        Creates a chunk of SQL to be used in the WHERE clause that
        filters a dataset described by `source` to data within the
        geography described by `region`
        """
        # based on the region's type, pick which field in the source we want
        field_type = f'{region.TYPE}_field'
        source_region_field = getattr(self, field_type)
        return f"""
        "{source_region_field}" LIKE '{region.geoid}'
        """
