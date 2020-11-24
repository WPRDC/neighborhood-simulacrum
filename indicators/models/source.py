from typing import List, Union

from census import Census
from django.db import models
from polymorphic.models import PolymorphicModel

from geo.models import CensusGeography
from indicators.models.abstract import Described
from profiles.local_settings import CENSUS_API_KEY

DEFAULT_GEOM_FIELD = '_geom'


class Source(Described, PolymorphicModel):
    """ Base class that defines data sources """
    series = models.ManyToManyField('Series', related_name="sources")


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
        c = Census(CENSUS_API_KEY)
        if self.dataset == 'ACS5':
            return c.acs5
        if self.dataset == 'CEN':
            return c.sf1


class CKANSource(Source, PolymorphicModel):
    package_id = models.UUIDField()
    resource_id = models.UUIDField()

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
            try:
                return getattr(self, attr)
            except:
                continue
        return None


class CKANGeomSource(CKANSource):
    geom_field = models.CharField(
        max_length=100,
        default=DEFAULT_GEOM_FIELD,
        null=True,
        blank=True
    )


class CKANRegionalSource(CKANSource):
    blockgroup_field = models.CharField(max_length=100, null=True, blank=True)
    tract_field = models.CharField(max_length=100, null=True, blank=True)
    countysubdivision_field = models.CharField(max_length=100, null=True, blank=True)
    place_field = models.CharField(max_length=100, null=True, blank=True)
    neighborhood_field = models.CharField(max_length=100, null=True, blank=True)
