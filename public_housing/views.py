import dataclasses

from django.conf import settings
from django.db.models import QuerySet
from django.http import QueryDict
from rest_framework import viewsets, views, filters
from rest_framework.request import Request
from rest_framework.response import Response

from profiles.content_negotiation import GeoJSONContentNegotiation
from public_housing.models import ProjectIndex
from public_housing.serializers import (
    ProjectIndexSerializer,
    ProjectIndexBriefSerializer,
    ProjectIndexGeoJSONSerializer,
)

COMPLEX_QUERY_PARAMS = ['subsidy_expiration']


@dataclasses.dataclass
class ComplexQuery:
    query: str
    method: str
    params: list[str]

    def run(self, queryset: QuerySet['ProjectIndex']) -> QuerySet['ProjectIndex']:
        # methods used the querystrings should map directly to the static custom filter args in the model
        filter_method = getattr(ProjectIndex, f'filter_by_{self.query}')
        return filter_method(queryset, self.params, method=self.method)


def split_key(key: str, sep='__') -> tuple[str, str]:
    halves = key.split(sep)[0:1]
    if len(halves) > 1:
        return halves[0], halves[1]
    if len(halves):
        return halves[0], ''
    return '', ''


def parse_params(qd: QueryDict):
    """ Extracts specific queries to run from URL querystring """
    simple: dict[str] = {}
    complx: list[ComplexQuery] = []
    for key, value in qd.items():
        if key == 'search':  # handled by SearchFilter
            continue
        query, method = split_key(key)
        # filter out the complex queries
        if query in COMPLEX_QUERY_PARAMS:
            complx.append(ComplexQuery(query, method, value))
            continue
        # cast the values from the query as needed based on the method
        if method in ['lt', 'gt', 'lte', 'gte']:
            simple[key] = float(value)
        else:
            simple[key] = value
    return simple, complx


class ProjectViewSet(viewsets.ModelViewSet):
    # queryset = ProjectIndex.objects.all()
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['hud_property_name', ]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectIndexBriefSerializer
        return ProjectIndexSerializer

    def get_queryset(self):
        queryset = ProjectIndex.objects.all()
        params = self.request.query_params
        if len(params.keys()):
            simple_filters, complex_filters = parse_params(params)
            # run complex filters first
            for complex_filter in complex_filters:
                queryset = complex_filter.run(queryset)
            # get simpler filters to send to partially filtered queryset
            return queryset.filter(**simple_filters)
        # default
        return queryset


class ProjectGeoJSONViewSet(viewsets.ModelViewSet):
    queryset = ProjectIndex.objects.all()
    serializer_class = ProjectIndexGeoJSONSerializer
    content_negotiation_class = GeoJSONContentNegotiation
    pagination_class = None


def kebab(string: str):
    return string.replace('_', '-').lower()


class ProjectVectorTileViewSet(views.APIView):
    """ Provides necessary settings to render in Mapbox.js """
    queryset = ProjectIndex.objects.all()

    def get(self, request: Request):
        map_view = settings.PUBLIC_HOUSING_PROJECT_LAYER_VIEW
        map_id = kebab(map_view)
        return Response({
            'source': {
                'id': map_id,
                'type': 'vector',
                'url': f'https://{request.META["SERVER_NAME"]}/tiles/maps.v_{map_view}.json'
            },
            'layers': [
                {
                    'id': f'{map_id}/marker',
                    'source': map_id,
                    'source-layer': f'maps.v_{map_view}',
                    'type': 'circle',
                }
            ],
            'extras': {
                'legend_items': [{
                    'variant': 'categorical',
                    'marker': 'black',
                    'label': 'Affordable Housing Projects'
                }]
            }
        })


class ProjectVectorTestTileViewSet(views.APIView):
    """ Provides necessary settings to render in Mapbox.js """
    queryset = ProjectIndex.objects.all()

    def get(self, request: Request):
        map_view = settings.PUBLIC_HOUSING_PROJECT_LAYER_VIEW
        map_id = kebab(map_view)
        return Response({
            'source': {
                'id': map_id,
                'type': 'vector',
                'url': f'https://{request.META["SERVER_NAME"]}/tiles/rpc/maps.test_func.json'
            },
            'layers': [
                {
                    'id': f'{map_id}/marker',
                    'source': map_id,
                    'source-layer': f'maps.test_func',
                    'type': 'circle',
                }
            ],
            'extras': {
                'legend_items': [{
                    'variant': 'categorical',
                    'marker': 'black',
                    'label': 'Affordable Housing Projects'
                }]
            }
        })
