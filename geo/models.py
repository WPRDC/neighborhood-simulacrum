import json
from abc import abstractmethod
from typing import List, Type

from django.contrib.gis.db import models
from polymorphic.models import PolymorphicModel

from geo.util import get_population, get_kid_population


class Geography(models.Model):
    """
    Abstract class for all Geographic regions
    """
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

    GEO_LEVELS = (
        ('NONE', 'N/A'),
        (BLOCK_GROUP, 'Block group'),
        (TRACT, 'Tract'),
        (COUNTY_SUBDIVISION, 'County Subdivision'),
        (COUNTY, 'County'),
        (PLACE, 'Place'),
        (PUMA, 'PUMA'),
        (STATE_HOUSE, 'State House'),
        (STATE_SENATE, 'State Senate'),
        (ZCTA, 'Zip Code Tabulation Area'),
        (NEIGHBORHOOD, 'Neighborhood'),
    )

    objects = models.Manager()

    child_geog_models: list[Type['Geography']] = []

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    geom = models.MultiPolygonField()
    geo_level = models.CharField(
        max_length=30,
        choices=GEO_LEVELS,
        default='NONE',
        blank=True,
    )

    @property
    def bbox(self):
        extent = self.geom.extent  # (xmin, ymin, xmax, ymax)
        return [list(extent[0:2]), list(extent[2:4])]

    @property
    def simple_geojson(self) -> dict:
        return {
            "type": "Feature",
            "geometry": json.loads(self.geom.json),
            "properties": {
                "name": self.name
            }
        }

    def __str__(self):
        return self.name


class CensusGeography(PolymorphicModel, Geography):
    """
    Base class for Census Geographies.
    """
    # Class fields
    TYPE: str
    TITLE: str

    ckan_resource: str
    base_zoom: int

    common_geoid = models.CharField(max_length=21, null=True, blank=True)
    affgeoid = models.CharField(max_length=21, unique=True)
    lsad = models.CharField(max_length=2)
    aland = models.BigIntegerField('Area (land)')
    awater = models.BigIntegerField('Area (water)')

    @property
    def title(self) -> str:
        return self.name

    @property
    def geog_type(self) -> str:
        return self.TYPE

    @property
    def geogID(self) -> str:
        """ Alias for geog_id. Workaround for camel case plugin to have ID instead of Id """
        return self.geog_id

    @property
    def geog_id(self) -> str:
        if self.geoid:
            return self.geoid
        raise NotImplementedError('Geographies without a `geoid` field must override `geog_id`')

    @property
    def population(self):
        return int(get_population(self))

    @property
    def kid_population(self):
        return int(get_kid_population(self))

    # Abstract properties
    @property
    @abstractmethod
    def title(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def subtitle(self) -> []:
        raise NotImplementedError

    @property
    @abstractmethod
    def hierarchy(self) -> List['CensusGeography']:
        raise NotImplementedError

    @property
    @abstractmethod
    def census_geo(self) -> dict:
        raise NotImplementedError


class BlockGroup(CensusGeography):
    TYPE = Geography.BLOCK_GROUP
    TITLE = "Block Group"
    carto_table = "census_blockgroup"

    ckan_resource = "b5f5480c-548d-46d8-b623-40a226d87517"

    child_geog_models = []

    base_zoom = 12

    geoid = models.CharField(max_length=12, primary_key=True)
    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    tractce = models.CharField(max_length=6)
    blkgrpce = models.CharField(max_length=1)

    @property
    def title(self):
        return f'Block Group {self.name}'

    @property
    def subtitle(self):
        return [{'title': geog.title, 'geoid': geog.geoid} for geog in self.hierarchy]

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


class Tract(CensusGeography):
    TYPE = Geography.TRACT
    TITLE = 'Tract'
    child_geog_models = [BlockGroup]

    geog_type = TYPE

    ckan_resource = "bb9a7972-981c-4026-8483-df8bdd1801c2"

    base_zoom = 10

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    tractce = models.CharField(max_length=6)

    @property
    def title(self):
        return f'Tract {self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

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


class CountySubdivision(CensusGeography):
    TYPE = Geography.COUNTY_SUBDIVISION
    TITLE = 'County Subdivision'
    carto_table = "census_county_subdivision"
    geog_type = TYPE

    ckan_resource = "8a5fc9dc-5eb9-4fe3-b60a-0366ad9b813b"

    base_zoom = 7

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    cousubfp = models.CharField(max_length=5)
    cousubns = models.CharField(max_length=8)

    child_geog_models = [Tract, BlockGroup]

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

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


class County(CensusGeography):
    TYPE = Geography.COUNTY
    TITLE = "County"
    child_geog_models = [CountySubdivision, Tract, BlockGroup]
    geog_type = TYPE

    ckan_resource = "8a5fc9dc-5eb9-4fe3-b60a-0366ad9b813b"

    base_zoom = 9

    geoid = models.CharField(max_length=12, primary_key=True)
    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=5)
    countyns = models.CharField(max_length=8)

    @property
    def census_geo(self):
        return {'for': f'county:{self.countyfp}',
                'in': f'state:{self.statefp}'}

    @property
    def title(self):
        return f'{self.name} County'

    @property
    def subtitle(self):
        return ''

    @property
    def hierarchy(self):
        return []

    class Meta:
        verbose_name_plural = "Counties"

    def __str__(self):
        return f'{self.name} County'


class ZipCodeTabulationArea(CensusGeography):
    TYPE = Geography.ZCTA
    TILE = 'Zip Code'
    child_geog_models = []

    zctace = models.CharField(max_length=5)
    geoid = models.CharField(max_length=5)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

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


class Neighborhood(CensusGeography):
    TYPE = Geography.NEIGHBORHOOD
    TITLE = 'Neighborhood'
    child_geog_models = [BlockGroup]

    geoid = models.CharField(max_length=12, primary_key=True)

    @property
    def countyfp(self):
        return '42003'

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

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


# Todo: Use these
class Place(CensusGeography):
    TYPE = "place"
    TITLE = 'Place'
    carto_table = 'census_place'
    geog_type = TYPE

    ckan_resource = "69d24a7a-421f-4e0b-8ee9-a91e46b116a8"

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    placefp = models.CharField(max_length=5)
    placens = models.CharField(max_length=8)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

    @property
    def hierarchy(self):
        return []

    @property
    def census_geo(self):
        return {'for': f'county subdivision:{self.cousubfp}',
                'in': f'state:{self.statefp} county:{self.countyfp}'}

    @property
    def census_geo(self):
        return {'for': f'tract:{self.placefp}',
                'in': f'state:{self.statefp}'}

    class Meta:
        verbose_name_plural = "Places"

    def __str__(self):
        return f'Place {self.geoid}'


class Puma(CensusGeography):
    TYPE = "puma"
    TITLE = "PUMA"
    carto_table = 'census_puma'
    geog_type = TYPE

    ckan_resource = "6eac8237-5275-4131-a9e6-a26494b22be2"

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    pumace = models.CharField(max_length=5)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

    @property
    def hierarchy(self):
        return []

    @property
    def census_geo(self):
        return {'for': f'tract:{self.pumace}',
                'in': f'state:{self.statefp}'}

    class Meta:
        verbose_name = "PUMA"
        verbose_name_plural = "PUMAS"

    def __str__(self):
        return f'PUMA {self.geoid}'


class SchoolDistrict(CensusGeography):
    TYPE = "schoolDistrict"
    TITLE = "School District"
    carto_table = 'census_school_districts'
    geog_type = TYPE

    ckan_resource = '35e9b048-c9fb-4412-a9d8-a751f975eb2a'

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    unsdlea = models.CharField(max_length=5)
    placens = models.CharField(max_length=8)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

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


class StateHouse(CensusGeography):
    TYPE = "stateHouse"
    TITLE = "State House"
    carto_table = 'census_pa_house'
    geog_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    sldlst = models.CharField(max_length=5)

    lsy = models.CharField(max_length=4)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

    @property
    def hierarchy(self):
        return []

    @property
    def census_geo(self):
        return {'for': f'tract:{self.sldlst}',
                'in': f'state:{self.statefp}'}

    class Meta:
        verbose_name = "State House District"
        verbose_name_plural = "State House Districts"

    def __str__(self):
        return f'State House - {self.geoid}'


class StateSenate(CensusGeography):
    TYPE = "stateSenate"
    TITLE = "State Senate"
    carto_table = 'census_pa_senate'
    geog_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    sldust = models.CharField(max_length=5)

    lsy = models.CharField(max_length=4)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([geog.title for geog in self.hierarchy])

    @property
    def hierarchy(self):
        return []

    @property
    def census_geo(self):
        return {'for': f'tract:{self.sldust}',
                'in': f'state:{self.statefp}'}

    class Meta:
        verbose_name = "State Senate District"
        verbose_name_plural = "State Senate Districts"
