from dataclasses import dataclass, field
from enum import Enum
from typing import Type, Union, Optional, List, TYPE_CHECKING

from django.conf import settings
from django.contrib.gis.db.models import Union as GeoUnion
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework.request import Request

from geo.models import Tract, County, BlockGroup, CountySubdivision, CensusGeography, SchoolDistrict, Neighborhood, \
    ZipCodeTabulationArea

if TYPE_CHECKING:
    from indicators.models import Variable, Variable, DataViz

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
class ErrorResponse:
    level: ErrorLevel
    message: Optional[str] = None

    def as_dict(self):
        return {
            'status': self.level.name,
            'level': self.level.value,
            'message': self.message,
        }


@dataclass
class DataResponse:
    data: Optional[Union[List[dict], dict]]
    options: dict = field(default_factory={})
    error: ErrorResponse = ErrorResponse(ErrorLevel.OK)

    def as_dict(self):
        return {
            'data': self.data,
            'options': self.options,
            'error': self.error.as_dict()
        }


# Functions
# =-=-=-=-=
def limit_to_geo_extent(geog_type: Type['CensusGeography']) -> QuerySet['CensusGeography']:
    """ Returns a queryset representing the geogs for `geog_type` that fit within project extent. """
    extent = County.objects \
        .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
        .aggregate(the_geom=GeoUnion('geom'))
    return geog_type.objects.filter(geom__coveredby=extent['the_geom'])


def get_geog_model(geog_type: str) -> Type[CensusGeography]:
    if geog_type in GEOG_MODEL_MAPPING:
        return GEOG_MODEL_MAPPING[geog_type]
    raise KeyError


def is_valid_geography_type(geog_type: str):
    return geog_type in GEOG_MODEL_MAPPING


def is_geog_data_request(request: Request) -> bool:
    """ Determines if a request should be responded to with calculated indicator data"""
    # for data visualization requests, data can be provided when a geog is defined
    # todo, handle other types.
    return GEOG_TYPE_LABEL in request.query_params and GEOG_ID_LABEL in request.query_params


def extract_geo_params(request: Request) -> (str, str):
    return request.query_params[GEOG_TYPE_LABEL], request.query_params[GEOG_ID_LABEL]


def get_geog_from_request(request: Request) -> CensusGeography:
    geog, geoid = extract_geo_params(request)
    geog_model = get_geog_model(geog)
    geog = geog_model.objects.get(geoid=geoid)
    return geog


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
