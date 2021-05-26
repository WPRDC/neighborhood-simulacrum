import json
from typing import Type

from django.conf import settings
from django.contrib.gis.db.models import QuerySet, Union
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, renderers
from rest_framework.exceptions import NotFound
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from geo.models import Geography, CensusGeography, County, BlockGroup
from geo.serializers import CensusGeographyDataMapSerializer
from indicators.models import Domain, Subdomain, Indicator, DataViz, Variable, TimeAxis, MiniMap
from indicators.serializers import DomainSerializer, IndicatorSerializer, SubdomainSerializer, \
    TimeAxisPolymorphicSerializer, VariablePolymorphicSerializer, DataVizWithDataSerializer, DataVizSerializer
from indicators.utils import is_geog_data_request, get_geog_from_request, ErrorResponse, ErrorLevel, \
    extract_geo_params, get_geog_model


class GeoJSONRenderer(renderers.BaseRenderer):
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


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SubdomainViewSet(viewsets.ModelViewSet):
    queryset = Subdomain.objects.all()
    serializer_class = SubdomainSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VariableViewSet(viewsets.ModelViewSet):
    queryset = Variable.objects.all()
    serializer_class = VariablePolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TimeAxisViewSet(viewsets.ModelViewSet):
    queryset = TimeAxis.objects.all()
    serializer_class = TimeAxisPolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DataVizViewSet(viewsets.ModelViewSet):
    queryset = DataViz.objects.all()

    def get_serializer_class(self):
        if is_geog_data_request(self.request):
            return DataVizWithDataSerializer
        return DataVizSerializer

    def get_serializer_context(self):
        context = super(DataVizViewSet, self).get_serializer_context()
        if is_geog_data_request(self.request):
            try:
                context['geography'] = get_geog_from_request(self.request)
            except Geography.DoesNotExist as e:
                print(e)  # todo: figure out how we should log stuff
                geo_type, geoid = extract_geo_params(self.request)
                context['error'] = ErrorResponse(ErrorLevel.ERROR,
                                                 f'Can\'t find "{geo_type}" with ID "{geoid}".').as_dict()
        return context

    # Cache requested url for each user for 2 minutes
    @method_decorator(cache_page(60 * 2))
    def retrieve(self, request, *args, **kwargs):
        return super(DataVizViewSet, self).retrieve(request, *args, **kwargs)


class GeoJSONWithDataView(APIView):
    permission_classes = [AllowAny, ]
    content_negotiation_class = GeoJSONContentNegotiation

    @method_decorator(cache_page(60 * 60 * 24))
    def get(self, request: Request, geog_type_id=None, data_viz_id=None, variable_id=None):
        try:
            geog_type: Type[CensusGeography] = get_geog_model(geog_type_id)
            data_viz: MiniMap = DataViz.objects.get(pk=data_viz_id)
            variable: Variable = Variable.objects.get(pk=variable_id)
            time_part = data_viz.time_axis.time_parts[0]
        except KeyError as e:
            # when the geog is wrong todo: make 400 malf
            #  ormed with info on available geo types
            raise NotFound
        except ObjectDoesNotExist as e:
            raise NotFound

        if geog_type == BlockGroup:
            # todo: actually handle this error, then this case
            return Http404

        geojson = data_viz.get_map_data_geojson(geog_type, variable)

        if request.query_params.get('download', False):
            headers = {
                'Content-Disposition': f'attachment; filename="{data_viz.slug}:{variable.slug}:{geog_type.TYPE}.geojson"'
            }
            return Response(geojson, headers=headers, content_type='application/geo+json')

        return Response(geojson)
