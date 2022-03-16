from typing import Union

from django.conf import settings
from django.contrib.gis.db.models.functions import Centroid
from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import views, viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from profiles.content_negotiation import GeoJSONContentNegotiation
from public_housing.models import ProjectIndex, Watchlist
from public_housing.serializers import (
    ProjectIndexSerializer,
    ProjectIndexBriefSerializer,
    ProjectIndexGeoJSONSerializer, WatchlistSerializer, WatchlistDetailedSerializer,
)


def get_filtered_project_indices(request: Request) -> QuerySet[ProjectIndex]:
    queryset = ProjectIndex.objects \
        .annotate(centroid=Centroid('geom')) \
        .all()

    # Match filter form items from app's map page
    risk_level = request.query_params.get('risk-level')
    watchlist = request.query_params.get('watchlist')

    if watchlist:
        wl = Watchlist.objects.get(slug=watchlist)
        queryset = ProjectIndex.objects.filter(property_id__in=wl.items)

    if risk_level:
        queryset = ProjectIndex.filter_by_at_risk(queryset, lvl=risk_level)

    return queryset


class WatchlistViewSet(viewsets.ModelViewSet):
    serializer_class = WatchlistSerializer
    queryset = Watchlist.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return WatchlistSerializer
        return WatchlistDetailedSerializer


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

    def get(self, request: Request) -> Response:
        # use complete set of projects, filtering will be handled by the layer's filter property
        map_view = settings.PUBLIC_HOUSING_PROJECT_LAYER_VIEW
        map_id = kebab(map_view)

        # base marker layer, can have filter added if need be
        marker_layer = {
            'id': f'{map_id}/marker',
            'source': map_id,
            'source-layer': f'maps.v_{map_view}',
            'type': 'symbol',
            "sprite": "mapbox://sprites/stevendsaylor/ckd6ixslm00461iqqn1hltgs8/cgf87udw29dtg22hkck4yaevo",
            'layout': {
                'icon-image': 'project',
                'icon-size': 0.8,
                'icon-allow-overlap': True,
                'text-allow-overlap': True,
                'text-field': ['to-string', ['get', 'hud_property_name']],
                'text-offset': [0, 0.5],
                'text-anchor': 'top',
            },
            'paint': {
                'text-opacity': [
                    "interpolate",
                    ["linear"],
                    ["zoom"],
                    0, 0,  # at zoom 0, have 0 opacity
                    14, 0,  # at zoom 14, have 0 but start to go up quickly
                    16, 1,
                    22, 1
                ]
            }
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
