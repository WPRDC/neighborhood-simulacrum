from abc import abstractmethod
from typing import List

from django.contrib.gis.db import models
from polymorphic.models import PolymorphicModel

from profiles.abstract_models import Described


class Geography(models.Model):
    """
    Abstract class to provide geographic data.
    """
    geom = models.MultiPolygonField()
    mini_geom = models.MultiPolygonField(null=True)
    geom_webmercator = models.MultiPolygonField(srid=3857, null=True)
    in_extent = models.BooleanField(null=True, blank=True, editable=False)

    @property
    def bbox(self):
        extent = self.geom.extent  # (xmin, ymin, xmax, ymax)
        return [list(extent[0:2]), list(extent[2:4])]

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.geom_webmercator:
            self.geom_webmercator = self.geom.transform(3857, clone=True)
        super(Geography, self).save(*args, **kwargs)


class AdminRegion(PolymorphicModel, Geography):
    """
    Base class for Administrative Regions or other areas of interest that can be described with available data.
    """
    # Class fields
    geog_type: str
    geog_type_title: str

    type_description: str
    ckan_resource: str
    base_zoom: int

    name = models.CharField(max_length=200)
    # Better formatted name than what's in the data. (e.g. Allegheny County instead of just Allegheny)
    display_name = models.CharField(max_length=200, null=True, blank=True)

    # A unique geoid.  `geoid` for census geographies.
    common_geoid = models.CharField(max_length=21, null=True, blank=True)

    @property
    def geog_path(self, separator='/') -> str:
        return f'{self.geog_type}{separator}{self.common_geoid}'

    @property
    def title(self) -> str:
        if self.display_name:
            return self.display_name
        return self.name

    @property
    def geogID(self) -> str:
        """ Alias for geog_id. Workaround for camel case plugin to have ID instead of Id """
        return self.common_geoid

    @property
    @abstractmethod
    def hierarchy(self) -> List['AdminRegion']:
        raise NotImplementedError

    def save(self, *args, **kwargs):
        super(AdminRegion, self).save(*args, **kwargs)


class CensusGeography(models.Model):
    """ Abstract base class that provides common census/acs geography details. """
    BLOCK_GROUP = 'blockGroup'
    TRACT = 'tract'
    COUNTY_SUBDIVISION = 'countySubdivision'
    PLACE = 'place'
    PUMA = 'puma'
    SCHOOL_DISTRICT = 'schoolDistrict'
    STATE_HOUSE = 'stateHouse'
    STATE_SENATE = 'stateSenate'
    COUNTY = 'county'
    ZCTA = 'zcta'
    NEIGHBORHOOD = 'neighborhood'

    geoid = models.CharField(max_length=20)
    affgeoid = models.CharField(max_length=21, unique=True)

    lsad = models.CharField(max_length=2)
    aland = models.BigIntegerField('Area (land)')
    awater = models.BigIntegerField('Area (water)')

    @property
    @abstractmethod
    def census_geo(self) -> dict:
        raise NotImplementedError

    class Meta:
        abstract = True


class BlockGroup(AdminRegion, CensusGeography):
    geog_type = CensusGeography.BLOCK_GROUP
    geog_type_title = "Block Group"

    type_description = 'Smallest geographical unit w/ ACS sample data.'
    ckan_resource = "b5f5480c-548d-46d8-b623-40a226d87517"
    base_zoom = 12

    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    tractce = models.CharField(max_length=6)
    blkgrpce = models.CharField(max_length=1)

    @property
    def title(self):
        return f'Block Group {self.name}'

    @property
    def hierarchy(self):
        return [
            County.objects.get(geoid=f'{self.statefp}{self.countyfp}'),
            Tract.objects.get(geoid=f'{self.statefp}{self.countyfp}{self.tractce}')
        ]

    @property
    def census_geo(self):
        return {'for': f'block group:{self.blkgrpce}',
                'in': f'state:{self.statefp} county:{self.countyfp} tract:{self.tractce}'}

    def __str__(self):
        return f'Block Group {self.geoid}'

    class Meta:
        verbose_name_plural = "Block Groups"


class Tract(AdminRegion, CensusGeography):
    geog_type = CensusGeography.TRACT
    geog_type_title = 'Tract'

    type_description = "Drawn to encompass ~2500-8000 people"
    ckan_resource = "bb9a7972-981c-4026-8483-df8bdd1801c2"
    base_zoom = 10

    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    tractce = models.CharField(max_length=6)

    @property
    def title(self):
        return f'Tract {self.name}'

    @property
    def hierarchy(self):
        return [County.objects.get(geoid=f'{self.statefp}{self.countyfp}')]

    @property
    def census_geo(self):
        return {'for': f'tract:{self.tractce}',
                'in': f'state:{self.statefp} county:{self.countyfp}'}

    class Meta:
        verbose_name_plural = "Tracts"

    def __str__(self):
        return f'Tract {self.geoid}'


class CountySubdivision(AdminRegion, CensusGeography):
    geog_type = CensusGeography.COUNTY_SUBDIVISION
    geog_type_title = 'County Subdivision'

    type_description = "Townships, municipalities, boroughs and cities."
    ckan_resource = "8a5fc9dc-5eb9-4fe3-b60a-0366ad9b813b"
    base_zoom = 7

    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    cousubfp = models.CharField(max_length=5)
    cousubns = models.CharField(max_length=8)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def hierarchy(self):
        return [County.objects.get(geoid=f'{self.statefp}{self.countyfp}')]

    @property
    def census_geo(self):
        return {'for': f'county subdivision:{self.cousubfp}',
                'in': f'state:{self.statefp} county:{self.countyfp}'}

    class Meta:
        verbose_name_plural = "County Subdivisions"

    def __str__(self):
        return f'County Subdivision {self.geoid}'


class County(AdminRegion, CensusGeography):
    geog_type = CensusGeography.COUNTY
    geog_type_title = "County"

    type_description = "Largest subdivision of a state."
    ckan_resource = "8a5fc9dc-5eb9-4fe3-b60a-0366ad9b813b"
    base_zoom = 9

    geoid = models.CharField(max_length=12, primary_key=True)
    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=5)
    countyns = models.CharField(max_length=8)

    @property
    def title(self):
        return f'{self.name} County'

    @property
    def hierarchy(self):
        return []

    @property
    def census_geo(self):
        return {'for': f'county:{self.countyfp}',
                'in': f'state:{self.statefp}'}

    class Meta:
        verbose_name_plural = "Counties"

    def __str__(self):
        return f'{self.name} County'


class ZipCodeTabulationArea(AdminRegion, CensusGeography):
    geog_type = CensusGeography.ZCTA
    geog_type_title = 'Zip Code'

    type_description = "The area covered by a postal Zip code."

    zctace = models.CharField(max_length=5)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def hierarchy(self):
        return []

    @property
    def census_geo(self):
        return {'for': f'tract:{self.sldust}',
                'in': f'state:{self.statefp}'}

    class Meta:
        verbose_name = "Zip Code Tabulation Area"
        verbose_name_plural = "Zip Code Tabulation Areas"


class SchoolDistrict(AdminRegion, CensusGeography):
    geog_type = "schoolDistrict"
    geog_type_title = "School District"

    type_description = 'Area served by a School District.'
    ckan_resource = '35e9b048-c9fb-4412-a9d8-a751f975eb2a'

    statefp = models.CharField(max_length=2)
    unsdlea = models.CharField(max_length=5)
    placens = models.CharField(max_length=8)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def hierarchy(self):
        return []

    @property
    def census_geo(self):
        return {'for': f'tract:{self.unsdlea}',
                'in': f'state:{self.statefp}'}

    class Meta:
        verbose_name_plural = "School Districts"

    def __str__(self):
        return f'{self.name} School District - {self.geoid}'


class Neighborhood(AdminRegion):
    geog_type = CensusGeography.NEIGHBORHOOD
    geog_type_title = 'Neighborhood'

    type_description = 'Official City of Pittsburgh neighborhood boundaries'

    @property
    def title(self):
        return f'{self.name}'

    @property
    def hierarchy(self):
        return []

    class Meta:
        verbose_name = "Neighborhood"
        verbose_name_plural = "Neighborhoods"
