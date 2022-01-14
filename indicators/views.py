from typing import Type

from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, filters
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from geo.models import AdminRegion, BlockGroup
from indicators.models import Domain, Subdomain, Indicator, DataViz, Variable, TimeAxis, MiniMap
from indicators.serializers import DomainSerializer, IndicatorSerializer, SubdomainSerializer, \
    TimeAxisPolymorphicSerializer, VariablePolymorphicSerializer, DataVizWithDataSerializer, \
    DataVizSerializer, DataVizBriefSerializer
from indicators.utils import is_geog_data_request, get_geog_from_request, ErrorRecord, ErrorLevel, \
    extract_geo_params, get_geog_model
from maps.models import DataLayer
from profiles.content_negotiation import GeoJSONContentNegotiation
from profiles.settings import VIEW_CACHE_TTL


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class SubdomainViewSet(viewsets.ModelViewSet):
    queryset = Subdomain.objects.all()
    serializer_class = SubdomainSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'


class VariableViewSet(viewsets.ModelViewSet):
    queryset = Variable.objects.all()
    serializer_class = VariablePolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class TimeAxisViewSet(viewsets.ModelViewSet):
    queryset = TimeAxis.objects.all()
    serializer_class = TimeAxisPolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class DataVizViewSet(viewsets.ModelViewSet):
    queryset = DataViz.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return DataVizBriefSerializer
        if is_geog_data_request(self.request):
            return DataVizWithDataSerializer
        return DataVizSerializer

    def get_serializer_context(self):
        context = super(DataVizViewSet, self).get_serializer_context()
        if is_geog_data_request(self.request):
            try:
                context['geography'] = get_geog_from_request(self.request)
            except AdminRegion.DoesNotExist as e:
                print(e)  # todo: figure out how we should log stuff
                geo_type, geoid = extract_geo_params(self.request)
                context['error'] = ErrorRecord(ErrorLevel.ERROR,
                                                 f'Can\'t find "{geo_type}" with ID "{geoid}".').as_dict()
        return context

    # Cache requested url for each user for 2 minutes
    @method_decorator(cache_page(VIEW_CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        return super(DataVizViewSet, self).retrieve(request, *args, **kwargs)


class GeoJSONWithDataView(APIView):
    permission_classes = [AllowAny, ]
    content_negotiation_class = GeoJSONContentNegotiation

    @method_decorator(cache_page(VIEW_CACHE_TTL))
    def get(self, request: Request, geog_type_id=None, data_viz_id=None, variable_id=None):
        try:
            geog_type: Type[AdminRegion] = get_geog_model(geog_type_id)
            data_viz: MiniMap = DataViz.objects.get(pk=data_viz_id)
            variable: Variable = Variable.objects.get(pk=variable_id)
            data_layer: DataLayer = data_viz.layers.all()[0].get_data_layer()
            geojson = data_layer.as_geojson()
        except KeyError as e:
            # when the geog is wrong todo: make 400 malformed with info on available geo types
            raise NotFound
        except ObjectDoesNotExist as e:
            raise NotFound

        if geog_type == BlockGroup:
            # todo: actually handle this error, then this case
            return Http404

        if request.query_params.get('download', False):
            headers = {
                'Content-Disposition': f'attachment; filename="{data_viz.slug}:{variable.slug}:{geog_type.geog_type}.geojson"'
            }
            return Response(geojson, headers=headers, content_type='application/geo+json')

        return Response(geojson)
