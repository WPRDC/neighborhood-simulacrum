import json
from typing import TYPE_CHECKING

from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, filters
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from maps.models import IndicatorLayer, MapLayer
from maps.serializers import DataLayerSerializer, IndicatorLayerDetailsSerializer, MapLayerSerializer, \
    MapLayerBriefSerializer
from profiles.content_negotiation import GeoJSONContentNegotiation

from django.conf import settings

if TYPE_CHECKING:
    pass


class DataLayerViewSet(viewsets.ModelViewSet):
    queryset = IndicatorLayer.objects.all()
    serializer_class = DataLayerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]

    def get_serializer_class(self):
        if self.action == 'list':
            return DataLayerSerializer
        return IndicatorLayerDetailsSerializer

    media_type = 'application/geo+json'
    format = 'geojson'

    @method_decorator(cache_page(settings.VIEW_CACHE_TTL))
    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps(data)


class GeoJSONDataLayerView(APIView):
    permission_classes = [AllowAny, ]
    content_negotiation_class = GeoJSONContentNegotiation

    @method_decorator(cache_page(settings.VIEW_CACHE_TTL))
    def get(self, request: Request, map_slug=None):
        try:
            data_layer: IndicatorLayer = IndicatorLayer.objects.get(slug=map_slug)
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


class MapLayerViewSet(viewsets.ModelViewSet):
    queryset = MapLayer.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    filter_backends = [filters.SearchFilter, ]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return MapLayerBriefSerializer
        return MapLayerSerializer
