import json
from typing import Type, TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, filters
from rest_framework.exceptions import NotFound
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from indicators.models import Variable, DataViz
from indicators.utils import get_geog_model
from indicators.views import GeoJSONRenderer
from maps.models import DataLayer
from maps.serializers import DataLayerSerializer, DataLayerDetailsSerializer
from profiles.settings import VIEW_CACHE_TTL

if TYPE_CHECKING:
    from geo.models import CensusGeography
    from indicators.models.viz import MiniMap


class DataLayerViewSet(viewsets.ModelViewSet):
    queryset = DataLayer.objects.all()
    serializer_class = DataLayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]

    def get_serializer_class(self):
        if self.action == 'list':
            return DataLayerSerializer
        return DataLayerDetailsSerializer

    media_type = 'application/geo+json'
    format = 'geojson'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps(data)


class GeoJSONContentNegotiation(BaseContentNegotiation):
    """
    Custom content negotiation scheme for GeoJSON files.

    `GeoJSONRenderer` is used for downloading geojson files
    `JSONRenderer` is used for ajax calls.
    """

    def select_parser(self, request, parsers):
        return super(GeoJSONContentNegotiation, self).select_parser(request, parsers)

    def select_renderer(self, request: Request, renderers, format_suffix=None):
        renderer = renderers[0]
        if request.query_params.get('download', False):
            renderer = GeoJSONRenderer()
        return renderer, renderer.media_type


class GeoJSONDataLayerView(APIView):
    permission_classes = [AllowAny, ]
    content_negotiation_class = GeoJSONContentNegotiation

    @method_decorator(cache_page(VIEW_CACHE_TTL))
    def get(self, request: Request, map_slug=None):
        try:
            data_layer: DataLayer = DataLayer.objects.get(slug=map_slug)
            geojson = data_layer.as_geojson()
        except KeyError as e:
            # when the geog is wrong todo: make 400 malformed with info on available geo types
            raise NotFound
        except ObjectDoesNotExist as e:
            raise NotFound

        if request.query_params.get('download', False):
            headers = {
                'Content-Disposition': f'attachment; filename="{map_slug}.geojson"'
            }
            return Response(geojson, headers=headers, content_type='application/geo+json')

        return Response(geojson)
