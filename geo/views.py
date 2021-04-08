from typing import Type

from django.conf import settings
from django.contrib.gis.db.models import Union
from rest_framework import viewsets, views, response, serializers
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geo.models import CensusGeography, Tract, County, CountySubdivision, BlockGroup
from geo.serializers import CensusGeographyPolymorphicSerializer, CensusGeographyBriefSerializer, \
    CensusGeographySerializer
from geo.util import all_geogs_in_domain
from indicators.utils import is_geog_data_request, get_geog_from_request

DOMAIN = County.objects \
    .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
    .aggregate(the_geom=Union('geom'))


class CensusGeographyViewSet(viewsets.ModelViewSet):
    queryset = CensusGeography.objects.all()
    serializer_class = CensusGeographyPolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if is_geog_data_request(self.request):
            geog = get_geog_from_request(self.request)
            return CensusGeography.objects.filter(pk=geog.pk)
        return self.queryset


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
