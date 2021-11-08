from typing import Type

from django.conf import settings
from rest_framework import viewsets, views, response, serializers, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from geo.models import AdminRegion, Tract, County, CountySubdivision, \
    BlockGroup, ZipCodeTabulationArea, Neighborhood
from geo.serializers import AdminRegionPolymorphicSerializer, \
    AdminRegionBriefSerializer, AdminRegionSerializer
from geo.util import all_geogs_in_extent
from indicators.utils import is_geog_data_request, get_geog_from_request, get_geog_model


class GetGeog(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if is_geog_data_request(request):
            geog = get_geog_from_request(request)
            data = AdminRegionPolymorphicSerializer(geog).data
            return response.Response(data)
        return response.Response()


class AdminRegionViewSet(viewsets.ModelViewSet):
    model: Type['AdminRegion']
    brief_serializer_class: [serializers.Serializer] = AdminRegionBriefSerializer
    detailed_serializer_class: [serializers.Serializer] = AdminRegionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'global_geoid']
    lookup_field = 'global_geoid'

    def get_queryset(self):
        return all_geogs_in_extent(self.model)

    def get_serializer_class(self):
        if self.request.query_params.get('details', False):
            return self.detailed_serializer_class
        return self.brief_serializer_class


class TractViewSet(AdminRegionViewSet):
    model = Tract


class BlockGroupViewSet(AdminRegionViewSet):
    model = BlockGroup


class CountySubdivisionViewSet(AdminRegionViewSet):
    model = CountySubdivision


class CountyViewSet(AdminRegionViewSet):
    model = County


class NeighborhoodViewSet(AdminRegionViewSet):
    model = Neighborhood


class ZipCodeViewSet(AdminRegionViewSet):
    model = ZipCodeTabulationArea


@api_view(http_method_names=['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def geog_list(request):
    records = []

    for type_str in settings.AVAILABLE_GEOG_TYPES:
        geog: Type[AdminRegion] = get_geog_model(type_str)
        # fixme: this seems like such a waste
        geog_record = geog.objects.all()[0].get_menu_record(AdminRegionBriefSerializer)
        records.append(geog_record)
    return Response(records)
