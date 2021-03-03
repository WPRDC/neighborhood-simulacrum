from typing import Type

from rest_framework.permissions import AllowAny
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view, permission_classes
from django.contrib.gis.db.models import GeometryField, QuerySet, Func, Union
from django.http import Http404, JsonResponse, HttpResponse
import json
from rest_framework import viewsets
from rest_framework.exceptions import APIException, NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.conf import settings
from rest_framework.response import Response

from geo.models import Geography, CensusGeography, County, BlockGroup
from geo.serializers import CensusGeographyDataMapSerializer
from indicators.models import Domain, Subdomain, Indicator, DataViz, Variable, TimeAxis
from indicators.serializers import (DomainSerializer, IndicatorSerializer, SubdomainSerializer,
                                    TimeAxisPolymorphicSerializer)
from indicators.serializers.variable import VariablePolymorphicSerializer
from indicators.serializers.viz import DataVizWithDataPolymorphicSerializer, DataVizPolymorphicSerializer
from indicators.utils import (is_region_data_request, get_region_from_request,
                              ErrorResponse, ErrorLevel, extract_geo_params,
                              get_region_model)


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
        if is_region_data_request(self.request):
            return DataVizWithDataPolymorphicSerializer
        return DataVizPolymorphicSerializer

    def get_serializer_context(self):
        context = super(DataVizViewSet, self).get_serializer_context()
        if is_region_data_request(self.request):
            try:
                context['geography'] = get_region_from_request(self.request)
            except Geography.DoesNotExist as e:
                print(e)  # todo: figure out how we should log stuff
                geo_type, geoid = extract_geo_params(self.request)
                context['error'] = ErrorResponse(ErrorLevel.ERROR,
                                                 f'Can\'t find "{geo_type}" with ID "{geoid}".').as_dict()
        return context


@api_view()
@permission_classes((AllowAny,))
def map_data(request, geog_type_id=None, data_viz_id=None, variable_id=None):
    """
    Custom view to serve Mapbox Vector Tiles for the custom polygon model.
    """
    # get geography from request
    try:
        geog_type: Type[CensusGeography] = get_region_model(geog_type_id)
        data_viz: DataViz = DataViz.objects.get(pk=data_viz_id)
        variable: Variable = Variable.objects.get(pk=variable_id)
        time_part = data_viz.time_axis.time_parts[0]
    except KeyError as e:
        # when the geog is wrong todo: make 400 malformed with info on available geo types
        raise NotFound
    except ObjectDoesNotExist as e:
        raise NotFound

    if geog_type == BlockGroup:
        # todo: actually handle this error, then this case
        return Http404

    serializer_context = {'data': variable.get_layer_data(data_viz, geog_type)}

    domain = County.objects \
        .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
        .aggregate(the_geom=Union('geom'))

    geogs: QuerySet['CensusGeography'] = geog_type.objects.filter(geom__coveredby=domain['the_geom'])
    geojson = CensusGeographyDataMapSerializer(geogs, many=True, context=serializer_context).data

    return Response(geojson)


# def mvt_tiles(request, geog_type_id=None, data_viz_id=None, variable_id=None, zoom=None, x=None, y=None):
#     """
#     Custom view to serve Mapbox Vector Tiles for the custom polygon model.
#     """
#     if None in (geog_type_id, data_viz_id, variable_id, zoom, x, y):
#         raise Http404()
#
#     # get geography from request
#     geog_type: CensusGeography = get_region_model(geog_type_id)
#     data_viz: DataViz = DataViz.objects.get(pk=data_viz_id)
#     variable: Variable = Variable.objects.get(pk=variable_id)
#
#     if not variable or not DataViz or not geog_type:
#         raise Http404()
#
#     time_part = data_viz.time_axis.time_parts[0]
#     serializer_context = {'variable': variable, 'time_part': time_part}
#
#     # check session for tile index
#     tile_index_key = ''
#     tile_index = request.session.get(tile_index_key, None)
#     if not tile_index:
#         # create the tile_index
#         # limit any query to select counties
#         domain = County.objects \
#             .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
#             .aggregate(the_geom=Union('geom'))
#         geogs: QuerySet['CensusGeography'] = geog_type.objects.filter(geom__coveredby=domain['the_geom'])
#         geojson = CensusGeographyDataMapSerializer(geogs, many=True, context=serializer_context).data
#         tile_index = geojson2vt(geojson, {})
#
#     tile = tile_index.get_tile(zoom, x, y).features
#
#     return HttpResponse(bytes(tile), content_type="application/x-protobuf")