from functools import reduce
from typing import Type, Union, Optional, List, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

from django.contrib.gis.geos import Polygon
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, OuterRef
from rest_framework.request import Request

from census_data.models import CensusValue
from geo.models import Tract, County, BlockGroup, CountySubdivision, CensusGeography

if TYPE_CHECKING:
    from indicators.models import Variable, CensusVariable, Variable, DataViz, CKANVariable, TimeAxis

# Constants
# =-=-=-=-=

CKAN_API_BASE_URL = 'https://data.wprdc.org/api/3/'
DATASTORE_SEARCH_SQL_ENDPOINT = 'action/datastore_search_sql'

REGION_TYPE_LABEL = 'regionType'
REGION_ID_LABEL = 'regionID'

VARIABLE_ID_LABEL = 'var'
DATA_VIZ_ID_LABEL = 'viz'

GEOG_MODEL_MAPPING = {
    'tract': Tract,
    'county': County,
    'blockGroup': BlockGroup,
    'countySubdivision': CountySubdivision,
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
    # todo: use generic types here
    data: Optional[Union[List[dict], dict, list,]]
    error: ErrorResponse

    def as_dict(self):
        return {
            'data': self.data,
            'error': self.error.as_dict()
        }


# Functions
# =-=-=-=-=

def get_region_model(region_type: str) -> Type[CensusGeography]:
    if region_type in GEOG_MODEL_MAPPING:
        return GEOG_MODEL_MAPPING[region_type]
    raise KeyError


def is_valid_geography_type(region_type: str):
    return region_type in GEOG_MODEL_MAPPING


def is_region_data_request(request: Request) -> bool:
    """ Determines if a request should be responded to with calculated indicator data"""
    # for data visualization requests, data can be provided when a region is defined
    # todo, handle other types.
    return REGION_TYPE_LABEL in request.query_params and REGION_ID_LABEL in request.query_params


def extract_geo_params(request: Request) -> (str, str):
    return request.query_params[REGION_TYPE_LABEL], request.query_params[REGION_ID_LABEL]


def get_region_from_request(request: Request) -> CensusGeography:
    region, geoid = extract_geo_params(request)
    region_model = get_region_model(region)
    region = region_model.objects.get(geoid=geoid)
    return region


def get_region_model_from_request(request: Request) -> Type[Union[Tract, County, BlockGroup, CountySubdivision]]:
    region = extract_geo_params(request)[0]
    region_model = get_region_model(region)
    return region_model


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

