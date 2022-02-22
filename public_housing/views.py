from typing import Union

from django.conf import settings
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import views, viewsets, filters
from rest_framework.request import Request
from rest_framework.response import Response

from profiles.content_negotiation import GeoJSONContentNegotiation
from public_housing.models import ProjectIndex
from public_housing.serializers import (
    ProjectIndexSerializer,
    ProjectIndexBriefSerializer,
    ProjectIndexGeoJSONSerializer,
)


def get_filtered_project_indices(request: Request) -> QuerySet[ProjectIndex]:
    queryset = ProjectIndex.objects.all()

    # Match filter form items from app's map page
    risk_level = request.query_params.get('risk-level')
    if risk_level:
        queryset = ProjectIndex.filter_by_at_risk(queryset, lvl=risk_level)

    return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    """
    Standard REST model viewset for Housing Projects.
    """
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['hud_property_name', ]

    def get_serializer_class(self) -> type(Union[ProjectIndexSerializer, ProjectIndexBriefSerializer]):
        if self.action == 'list':
            return ProjectIndexBriefSerializer
        return ProjectIndexSerializer

    def get_queryset(self) -> QuerySet[ProjectIndex]:
        return get_filtered_project_indices(self.request)


class ProjectGeoJSONViewSet(viewsets.ModelViewSet):
    """
    Viewset that allows for GeoJSON file downloads and connections to third party mapping tools.
    """
    queryset = ProjectIndex.objects.all()
    serializer_class = ProjectIndexGeoJSONSerializer
    content_negotiation_class = GeoJSONContentNegotiation
    pagination_class = None

    def get_queryset(self) -> QuerySet[ProjectIndex]:
        return get_filtered_project_indices(self.request)


def kebab(string: str) -> str:
    return string.replace('_', '-').lower()


class ProjectVectorTileViewSet(views.APIView):
    """
    Provides necessary settings to render a mapbox-gl map plus additional settings for use with
      [@wprdc-widgets/map](https://github.com/WPRDC/frontend-libraries/tree/main/packages/%40wprdc-widgets/map)
      React component
    """

    def get_queryset(self) -> QuerySet[ProjectIndex]:
        return get_filtered_project_indices(self.request)

    @method_decorator(cache_page(settings.VIEW_CACHE_TTL))
    def get(self, request: Request) -> Response:
        # use complete set of projects, filtering will be handled by the layer's filter property
        map_view = settings.PUBLIC_HOUSING_PROJECT_LAYER_VIEW
        map_id = kebab(map_view)

        # base marker layer, can have filter added if need be
        marker_layer = {
            'id': f'{map_id}/marker',
            'source': map_id,
            'source-layer': f'maps.v_{map_view}',
            'type': 'circle',
        }

        # only filter if necessary
        if len(self.request.query_params.keys()):
            # get set of id's to filter by
            projects = self.get_queryset()
            ids = [project.id for project in projects]
            # only those with an id in `ids`
            # https://docs.mapbox.com/mapbox-gl-js/style-spec/expressions
            marker_layer = {
                **marker_layer,
                'filter': ['in', ['get', 'id'], ['literal', ids]]
            }

        return Response({
            'source': {
                'id': map_id,
                'type': 'vector',
                'url': f'https://{request.META["SERVER_NAME"]}/tiles/maps.v_{map_view}.json'
            },
            'layers': [
                marker_layer
            ],
            'extras': {
                'legend_items': [{
                    'key': 'ah-projects',
                    'variant': 'categorical',
                    'marker': 'black',
                    'label': 'Affordable Housing Projects'
                }]
            }
        })
