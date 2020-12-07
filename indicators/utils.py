from typing import Type, Union

from enum import Enum

from rest_framework.request import Request

from geo.models import CensusGeography, Tract, County, BlockGroup, CountySubdivision

CKAN_API_BASE_URL = 'https://data.wprdc.org/api/3/'
DATASTORE_SEARCH_SQL_ENDPOINT = 'action/datastore_search_sql'

REGION_TYPE_LABEL = 'regionType'
REGION_ID_LABEL = 'geoid'

REGION_MODEL_MAPPING = {
    'tract': Tract,
    'county': County,
    'blockgroup': BlockGroup,
    'countysubdivision': CountySubdivision,
}


class GeoIDFixes(Enum):
    AS_IS = 0  # keep zero just in case, the others are arbitrary
    LEFT_PAD = 1
    EXTRACT = 2

def get_region_model(region_type: str) -> Type[Union[Tract, County, BlockGroup, CountySubdivision]]:
    if region_type in REGION_MODEL_MAPPING:
        return REGION_MODEL_MAPPING[region_type]


def is_valid_region_query_request(request: Request) -> bool:
    """ Determines if a request shoudl be responded to with calculated indicator data"""
    # for data visualization requests, data can be provided when a region is defined
    # todo, handle other types.
    return REGION_TYPE_LABEL in request.query_params and REGION_ID_LABEL in request.query_params


def get_region_from_query_params(request: Request) -> CensusGeography:
    region = request.query_params[REGION_TYPE_LABEL]
    geoid = request.query_params[REGION_ID_LABEL]
    region_model = get_region_model(region)
    region = region_model.objects.get(geoid=geoid)
    return region
