from dataclasses import dataclass, field
from enum import Enum
from typing import Type, Union, Optional, TYPE_CHECKING, Mapping

import psycopg2.extras
from django.conf import settings
from django.contrib.gis.db.models import Union as GeoUnion
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.db.models import QuerySet
from rest_framework.request import Request

from geo.models import Tract, County, BlockGroup, CountySubdivision, AdminRegion, SchoolDistrict, Neighborhood, \
    ZipCodeTabulationArea

if TYPE_CHECKING:
    from indicators.models import Variable, Variable, DataViz
    from indicators.data import Datum

# Constants
# =-=-=-=-=
CKAN_API_BASE_URL = 'https://data.wprdc.org/api/3/'
DATASTORE_SEARCH_SQL_ENDPOINT = 'action/datastore_search_sql'

GEOG_TYPE_LABEL = 'geogType'
GEOG_ID_LABEL = 'geogID'

VARIABLE_ID_LABEL = 'var'
DATA_VIZ_ID_LABEL = 'viz'

GEOG_MODEL_MAPPING = {
    'tract': Tract,
    'county': County,
    'blockGroup': BlockGroup,
    'countySubdivision': CountySubdivision,
    'schoolDistrict': SchoolDistrict,
    'neighborhood': Neighborhood,
    'zcta': ZipCodeTabulationArea
}


# Types/Enums/Etc
# =-=-=-=-=-=-=-=
class ErrorLevel(Enum):
    OK = 0
    EMPTY = 1
    WARNING = 10
    ERROR = 100


@dataclass
class ErrorRecord:
    level: ErrorLevel
    message: Optional[str] = None
    record: Optional[Mapping] = None

    def as_dict(self):
        return {
            'status': self.level.name,
            'level': self.level.value,
            'message': self.message,
            'record': self.record
        }


@dataclass
class DataResponse:
    data: Optional[Union[list['Datum'], dict]]
    options: dict = field(default_factory=dict)
    error: ErrorRecord = ErrorRecord(ErrorLevel.OK)
    warnings: Optional[list[ErrorRecord]] = None

    def as_dict(self):
        return {
            'data': [datum.as_dict() for datum in self.data],
            'options': self.options,
            'error': self.error.as_dict(),
            'warnings': self.warnings
        }


# Functions
# =-=-=-=-=
def limit_to_geo_extent(geog_type: Type['AdminRegion']) -> QuerySet['AdminRegion']:
    """ Returns a queryset representing the geogs for `geog_type` that fit within project extent. """
    return geog_type.objects.filter(in_extent=True)


# noinspection SqlResolve
def save_extent():
    extent = County.objects \
        .filter(global_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
        .aggregate(the_geom=GeoUnion('geom'))
    extent_wkt = extent['the_geom'].wkt

    # noinspection PyUnresolvedReferences,PyProtectedMember
    cursor: 'psycopg2._psycopg.cursor'
    with connection.cursor() as cursor:
        cursor.execute("""DROP TABLE IF EXISTS "#extent";""")
        cursor.execute("""CREATE TABLE "#extent" (id varchar(63));""")
        cursor.execute("""SELECT AddGeometryColumn('#extent', 'geom', 4326, 'MultiPolygon', 2);""")
        cursor.execute("""INSERT INTO "#extent" 
                            VALUES ('default', ST_MPolyFromText(%s, 4326));""", (extent_wkt,))
        cursor.execute("""CREATE INDEX "#extent_index" ON "#extent" USING gist (geom);""")


def in_geo_extent(geog: 'AdminRegion') -> bool:
    return County.objects \
        .filter(global_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
        .aggregate(the_geom=GeoUnion('geom')).values('the_geom').contains(geog)


def get_geog_model(geog_type: str) -> Type[AdminRegion]:
    if geog_type in GEOG_MODEL_MAPPING:
        return GEOG_MODEL_MAPPING[geog_type]
    raise KeyError


def is_valid_geography_type(geog_type: str):
    return geog_type in GEOG_MODEL_MAPPING


def is_geog_data_request(request: Request) -> bool:
    """ Determines if a request should be responded to with calculated indicator data"""
    # for data visualization requests, data can be provided when a geog is defined
    return 'geog' in request.query_params


def extract_geo_params(request: Request) -> (str, str):
    return request.query_params[GEOG_TYPE_LABEL], request.query_params[GEOG_ID_LABEL]


def get_geog_from_request(request: Request) -> AdminRegion:
    slug = request.query_params.get('geog')
    return AdminRegion.objects.get(slug=slug)


def get_geog_model_from_request(request: Request) -> Type[Union[Tract, County, BlockGroup, CountySubdivision]]:
    geog = extract_geo_params(request)[0]
    geog_model = get_geog_model(geog)
    return geog_model


def get_data_viz_from_request(request: Request) -> Optional['Variable']:
    viz_id = request.query_params.get(DATA_VIZ_ID_LABEL, None)
    try:
        var = DataViz.objects.get(id=int(viz_id))
        return var
    except ObjectDoesNotExist:
        return None


def get_variable_from_request(request: Request) -> Optional['Variable']:
    var_id = request.query_params.get(VARIABLE_ID_LABEL, None)
    try:
        var = Variable.objects.get(id=int(var_id))
        return var
    except ObjectDoesNotExist:
        return None


def tile_bbox(z, x, y, srid=3857):
    """
    Returns GEOS Polygon object representing the bbox
    https://github.com/mapbox/postgis-vt-util/blob/master/src/TileBBox.sql
    """
    max_v = 20037508.34
    res = (max_v * 2) / (2 ** z)
    bbox = Polygon.from_bbox((
        -max_v + (x * res),
        max_v - (y * res),
        -max_v + (x * res) + res,
        max_v - (y * res) - res,
    ))
    bbox.srid = 3857
    if srid != 3857:
        bbox.transform(srid)
    return bbox
