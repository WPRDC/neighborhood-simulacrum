from abc import abstractmethod
from typing import List

from django.contrib.gis.db import models
from polymorphic.managers import PolymorphicManager
from polymorphic.models import PolymorphicModel

from geo.util import get_population, get_kid_population
from indicators.helpers import clean_sql


class Geography(models.Model):
    """
    Abstract class for all Geographic regions
    """
    BLOCK_GROUP = 'BLOCKGROUP'
    TRACT = 'TRACT'
    COUNTY_SUBDIVISION = 'COUNTY_SUBDIVISION'
    PLACE = 'PLACE'
    PUMA = 'PUMA'
    SCHOOL_DISTRICT = 'SCHOOL_DISTRICT'
    STATE_HOUSE = 'STATE_HOUSE'
    STATE_SENATE = 'STATE_SENATE'
    COUNTY = 'COUNTY'

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
        (SCHOOL_DISTRICT, 'School District'),
    )

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

    def __str__(self):
        return self.name


class CensusGeography(PolymorphicModel, Geography):
    """
    Base class for Census Geographies.
    """
    # Class fields
    TYPE: str
    TITLE: str
    carto_table: str
    carto_geoid_field: str = 'geoid'
    carto_geom_field: str = 'the_geom'
    carto_geom_webmercator_field: str = 'the_geom_webmercator'

    common_geoid = models.CharField(max_length=21, null=True, blank=True)
    affgeoid = models.CharField(max_length=21, unique=True)
    lsad = models.CharField(max_length=2)
    aland = models.BigIntegerField('Area (land)')
    awater = models.BigIntegerField('Area (water)')

    @property
    def region_type(self) -> str:
        return self.TYPE

    @property
    def regionID(self) -> str:
        """ Alias for region_id. Workaround for camel case plugin to have ID instead of Id """
        return self.region_id

    @property
    def region_id(self) -> str:
        if self.geoid:
            return self.geoid
        raise NotImplementedError('Geographies without a `geoid` field must override `region_id`')

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

    @property
    def carto_geom_sql(self):
        return clean_sql(f"""
                    SELECT {self.carto_geom_field}
                    FROM {self.carto_table}
                    WHERE {self.carto_geoid_field} = '{self.geoid}'
                    """)

    @property
    def carto_sql(self):
        return clean_sql(f"""
                    SELECT {self.carto_geom_field}, {self.carto_geom_webmercator_field}
                    FROM {self.carto_table}
                    WHERE {self.carto_geoid_field} = '{self.geoid}'
                    """)

    @property
    def population(self):
        return get_population(self)

    @property
    def kid_population(self):
        return get_kid_population(self)


class BlockGroup(CensusGeography):
    TYPE = "blockGroup"
    TITLE = "Block Group"
    carto_table = "census_blockgroup"

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
        return [{'title': region.title, 'geoid': region.geoid} for region in self.hierarchy]

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
    TYPE = "tract"
    TITLE = 'Tract'
    carto_table = "census_tract"
    region_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    tractce = models.CharField(max_length=6)

    @property
    def title(self):
        return f'Tract {self.name}'

    @property
    def subtitle(self):
        return '/'.join([region.title for region in self.hierarchy])

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
    TYPE = "countyGubdivision"
    TITLE = 'County Subdivision'
    carto_table = "census_county_subdivision"
    region_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    countyfp = models.CharField(max_length=3)
    cousubfp = models.CharField(max_length=5)
    cousubns = models.CharField(max_length=8)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([region.title for region in self.hierarchy])

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
    TYPE = "county"
    TITLE = "County"
    carto_table = 'census_county'
    region_type = TYPE

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


# Todo: Use these
class Place(CensusGeography):
    TYPE = "place"
    TITLE = 'Place'
    carto_table = 'census_place'
    region_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    placefp = models.CharField(max_length=5)
    placens = models.CharField(max_length=8)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([region.title for region in self.hierarchy])

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
    region_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    pumace = models.CharField(max_length=5)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([region.title for region in self.hierarchy])

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
    region_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    unsdlea = models.CharField(max_length=5)
    placens = models.CharField(max_length=8)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([region.title for region in self.hierarchy])

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
    region_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    sldlst = models.CharField(max_length=5)

    lsy = models.CharField(max_length=4)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([region.title for region in self.hierarchy])

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
    region_type = TYPE

    geoid = models.CharField(max_length=12, primary_key=True)

    statefp = models.CharField(max_length=2)
    sldust = models.CharField(max_length=5)

    lsy = models.CharField(max_length=4)

    @property
    def title(self):
        return f'{self.name}'

    @property
    def subtitle(self):
        return '/'.join([region.title for region in self.hierarchy])

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
