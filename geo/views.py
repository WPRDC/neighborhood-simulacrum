from django.conf import settings
from django.contrib.gis.db.models import Union
from rest_framework import viewsets, views, response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geo.models import CensusGeography, Tract, County, CountySubdivision, BlockGroup
from geo.serializers import CensusGeographyPolymorphicSerializer, CensusGeographyBriefSerializer
from geo.util import all_geogs_in_domain
from indicators.utils import is_region_data_request, get_region_from_request

DOMAIN = County.objects \
    .filter(common_geoid__in=settings.AVAILABLE_COUNTIES_IDS) \
    .aggregate(the_geom=Union('geom'))

class CensusGeographyViewSet(viewsets.ModelViewSet):
    queryset = CensusGeography.objects.all()
    serializer_class = CensusGeographyPolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if is_region_data_request(self.request):
            region = get_region_from_request(self.request)
            return CensusGeography.objects.filter(pk=region.pk)
        return self.queryset


class GetRegion(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if is_region_data_request(request):
            region = get_region_from_request(request)
            data = CensusGeographyPolymorphicSerializer(region).data
            return response.Response(data)
        return response.Response()


class TractViewSet(viewsets.ModelViewSet):
    queryset = all_geogs_in_domain(Tract, DOMAIN)
    serializer_class = CensusGeographyBriefSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class BlockGroupViewSet(viewsets.ModelViewSet):
    queryset = all_geogs_in_domain(BlockGroup, DOMAIN)
    serializer_class = CensusGeographyBriefSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CountySubdivisionViewSet(viewsets.ModelViewSet):
    queryset = all_geogs_in_domain(CountySubdivision, DOMAIN)
    serializer_class = CensusGeographyBriefSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CountyViewSet(viewsets.ModelViewSet):
    queryset = all_geogs_in_domain(County, DOMAIN)
    serializer_class = CensusGeographyBriefSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
