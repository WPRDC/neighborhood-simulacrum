from typing import Type, Union, Optional, List, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

from rest_framework.request import Request
from geo.models import Tract, County, BlockGroup, CountySubdivision, CensusGeography

if TYPE_CHECKING:
    from indicators.models import CensusVariable, TimeAxis

# Constants
# =-=-=-=-=

CKAN_API_BASE_URL = 'https://data.wprdc.org/api/3/'
DATASTORE_SEARCH_SQL_ENDPOINT = 'action/datastore_search_sql'

REGION_TYPE_LABEL = 'regionType'
REGION_ID_LABEL = 'regionID'

REGION_MODEL_MAPPING = {
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
    message: Optional[str]

    def as_dict(self):
        return {
            'status': self.level.name,
            'level': self.level.value,
            'message': self.message,
        }


@dataclass
class DataResponse:
    data: Optional[Union[List[dict], dict]]
    error: ErrorResponse

    def as_dict(self):
        return {
            'data': self.data,
            'error': self.error.as_dict()
        }


# Functions
# =-=-=-=-=

def get_region_model(region_type: str) -> Type[Union[Tract, County, BlockGroup, CountySubdivision]]:
    if region_type in REGION_MODEL_MAPPING:
        return REGION_MODEL_MAPPING[region_type]


def is_valid_geography_type(region_type: str):
    return region_type in REGION_MODEL_MAPPING


def is_region_data_request(request: Request) -> bool:
    """ Determines if a request should be responded to with calculated indicator data"""
    # for data visualization requests, data can be provided when a region is defined
    # todo, handle other types.
    return REGION_TYPE_LABEL in request.query_params and REGION_ID_LABEL in request.query_params


def extract_geo_params(request: Request) -> (str, str):
    return request.query_params[REGION_TYPE_LABEL], request.query_params[REGION_ID_LABEL]


def get_region_from_query_params(request: Request) -> CensusGeography:
    region, geoid = extract_geo_params(request)
    region_model = get_region_model(region)
    region = region_model.objects.get(geoid=geoid)
    return region


