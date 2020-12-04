from typing import Union, List, Type

import requests
from census import Census, CensusException
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from rest_framework.request import Request

from geo.models import CensusGeography, Tract, County, BlockGroup, CountySubdivision
from indicators.models import (
    Indicator,
    CKANGeomSource,
    CensusSource,
    CensusVariable,
    CKANRegionalSource,
    Subdomain,
    MiniMap
)
from indicators.models import CensusValue
from profiles.settings import CENSUS_API_KEY

CKAN_API_BASE_URL = 'https://data.wprdc.org/api/3/'
DATASTORE_SEARCH_SQL_ENDPOINT = 'action/datastore_search_sql'

# Constants for hard-coded strings.
# TODO: move to central settings somehow.
# generally these don't need to be changed for specific deployments
_ALL_VARIABLES_LABEL = 'variables'
_VARIABLE_LABEL = 'variable'
_VALUE_LABEL = 'value'
_DATA_LABEL = 'data'
_DENOMS_LABEL = 'denoms'
_MINIMAPS_LABEL = 'maps'
REGION_TYPE_LABEL = 'regionType'
REGION_ID_LABEL = 'geoid'


def get_region_model(region_type: str) -> Type[Union[Tract, County, BlockGroup, CountySubdivision]]:
    REGION_MODEL_MAPPING = {
        'tract': Tract,
        'county': County,
        'blockgroup': BlockGroup,
        'countysubdivision': CountySubdivision,
    }
    if region_type in REGION_MODEL_MAPPING:
        return REGION_MODEL_MAPPING[region_type]


def get_census_variable_at_region(variable: CensusVariable, region: CensusGeography):
    c = Census(CENSUS_API_KEY)
    getter = None
    if variable.source.dataset == 'ACS5':
        getter = c.acs5
    if variable.source.dataset == 'CEN':
        getter = c.sf1

    formula_parts = variable.formula_parts
    return getter.get(formula_parts, region.census_geo)


def get_census_parts_at_region(parts, region, dataset):
    c = Census(CENSUS_API_KEY)
    getter = None
    if dataset == 'ACS5':
        getter = c.acs5
    if dataset == 'CEN':
        getter = c.sf1
    try:
        result = getter.get(list(parts), region.census_geo)
    except CensusException as e:
        print(e)
    return result


def serialize_domain(domain):
    return {
        'name': domain.name,
        'description': domain.description,
        'subdomains': [],
    }


def serialize_group(group: Subdomain):
    return {
        'name': group.name,
        'description': group.description,
        'indicators': [],
    }


def serialize_region(region: CensusGeography) -> dict:
    return {
        'regionType': region.TYPE,
        'geoid': region.geoid,
        'name': region.name,
        'title': region.title,
        'subtitle': region.subtitle,
    }


def serialize_indicator(indicator: Indicator):
    return {
        'name': indicator.name,
        'description': indicator.description,
        'longDescription': indicator.long_description,
        'limitations': indicator.limitations,
        'provenance': indicator.provenance,
        'years': indicator.years,
        'source': indicator.source,
        'importance': indicator.importance,
        'variables': [],
    }


def serialize_source(source: Union[CensusSource, CKANRegionalSource, CKANGeomSource]) -> dict:
    if type(source) in (CensusSource,):
        return {
            'datasource': source.dataset,
            'year': source.year,
        }
    else:
        return {
            'name': source.name,
            'title': source.title,
        }


def serialize_variable(variable: Union[CensusVariable]) -> dict:
    return {
        'name': variable.name,
        'title': variable.title,
        'units': variable.units,
        'unitNotes': variable.unit_notes,
        'description': variable.description,
        'indent': variable.indent,
        'data': {},
    }


def serialize_denom_variable(variable: Union[CensusVariable]) -> dict:
    return {
        'name': variable.name,
        'title': variable.title,
        'percentLabel': variable.percent_label,
        'data': {},
    }


def find_uncached_census_data(variables: QuerySet,
                              region: CensusGeography,
                              all_sources: List[Union[CKANGeomSource, CensusSource, CKANRegionalSource]]) -> None:
    """ separate variables based on their source and filter out the variables that are cached """
    lookup_formulas = {source: set() for source in all_sources}
    responses = {source: [] for source in all_sources}

    lookup_vars = set()

    for variable in variables.all():
        if type(variable) == CensusVariable:
            for part in variable.formula_parts:
                if not CensusValue.objects.filter(census_table=part, region=region):
                    # if the value isn't cached, add it to the query list
                    lookup_formulas[variable.source].update(variable.formula_parts)
                    # keep track of variables to join with the gotten data
                    lookup_vars.add(variable)

    # with all of the uncached variables found, look up the data for them
    for k, v in lookup_formulas.items():
        if not lookup_formulas[k]:
            continue
        responses[k] = get_census_parts_at_region(lookup_formulas[k], region, k.dataset)

    # ... and store them in the value table
    for variable in lookup_vars:
        variable._extract_values_from_api_response(region, responses)


def get_variable_data(variable_name: str, indicator: Indicator, region: CensusGeography):
    # need to use `filter` since there are multiple `variable` objects for the same real-world variable
    curr_variables = indicator.variable_set.filter(name=variable_name)

    # we only need to use the first one in this queryset, since it has the same meta data as the others.
    # the others will be the same variable, but with data pulled from different sources
    variable_dict = serialize_variable(curr_variables[0])
    denoms_dict = {}

    # collect the data for each `variable`
    for var in curr_variables:

        # store the primary values keyed by year
        variable_dict[_DATA_LABEL][var.source.year] = var.get_value_and_moe(region)

        for denom in var.denominators.all():
            denom_label = denom.name
            if denom_label not in denoms_dict:
                denoms_dict[denom_label] = serialize_denom_variable(denom)
            denoms_dict[denom_label][_DATA_LABEL][denom.source.year] = var.get_proportional_data(region, denom)

    # reconcile denoms_dict with main dict
    variable_dict[_DENOMS_LABEL] = []
    for k in denoms_dict:
        variable_dict[_DENOMS_LABEL].append(denoms_dict[k])

    return variable_dict


def get_minimap_data_for_region(minimap: MiniMap, region: CensusGeography) -> dict:
    return {
        'id': minimap.slug,
        'name': minimap.name,
        'query': minimap.get_sql_for_region(region),
        'layer': {'type': minimap.layer_type, 'paint': minimap.paint, 'layout': minimap.layout or {}},
        'regionQuery': region.carto_sql,
        'bbox': region.bbox,
    }


def get_all_minimap_data(indicator: Indicator, region: CensusGeography):
    minimaps = indicator.minimaps.all()
    result = []
    for minimap in minimaps:
        result.append(get_minimap_data_for_region(minimap, region))
    return result


def get_indicator_at_region(indicator: Indicator, region: CensusGeography):
    variables = indicator.variable_set.all()
    all_sources = CensusSource.objects.all()

    # find uncached variables and their formulas
    find_uncached_census_data(variables, region, all_sources)

    # the serialized indicator dict will serve as the root of all serialized data
    results = serialize_indicator(indicator)

    # use supplied variable order to have things in order for frontend
    for variable_name in indicator.variable_order:
        results[_ALL_VARIABLES_LABEL].append(get_variable_data(variable_name, indicator, region))

    results[_MINIMAPS_LABEL] = get_all_minimap_data(indicator, region)

    return results


# new stuff

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
