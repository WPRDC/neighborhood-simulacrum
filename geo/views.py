from typing import Type

from django.conf import settings
from django.contrib.gis.db.models import Union
from rest_framework import viewsets, views, response, serializers, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from geo.models import CensusGeography, Tract, County, CountySubdivision, BlockGroup, ZipCodeTabulationArea, \
    Neighborhood
from geo.serializers import CensusGeographyPolymorphicSerializer, CensusGeographyBriefSerializer, \
    CensusGeographySerializer
from geo.util import all_geogs_in_domain
from indicators.utils import is_geog_data_request, get_geog_from_request, get_geog_model

DOMAIN = County.objects \
    .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
    .aggregate(the_geom=Union('geom'))


class GetGeog(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if is_geog_data_request(request):
            geog = get_geog_from_request(request)
            data = CensusGeographyPolymorphicSerializer(geog).data
            return response.Response(data)
        return response.Response()


class CensusGeographyViewSet(viewsets.ModelViewSet):
    model: Type['CensusGeography']
    brief_serializer_class: [serializers.Serializer] = CensusGeographyBriefSerializer
    detailed_serializer_class: [serializers.Serializer] = CensusGeographySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'common_geoid']

    def get_queryset(self):
        return all_geogs_in_domain(self.model, DOMAIN)

    def get_serializer_class(self):
        if self.request.query_params.get('details', False):
            return self.detailed_serializer_class
        return self.brief_serializer_class



class TractViewSet(CensusGeographyViewSet):
    model = Tract


class BlockGroupViewSet(CensusGeographyViewSet):
    model = BlockGroup


class CountySubdivisionViewSet(CensusGeographyViewSet):
    model = CountySubdivision


class CountyViewSet(CensusGeographyViewSet):
    model = County


class NeighborhoodViewSet(CensusGeographyViewSet):
    model = Neighborhood


class ZipCodeViewSet(CensusGeographyViewSet):
    model = ZipCodeTabulationArea


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def geog_list(request):
    records = []

    for type_str in settings.AVAILABLE_GEOG_TYPES:
        geog: Type[CensusGeography] = get_geog_model(type_str)
        # fixme: this seems like such a waste
        geog_record = geog.objects.all()[0].get_menu_record()
        records.append(geog_record)
    return Response(records)
