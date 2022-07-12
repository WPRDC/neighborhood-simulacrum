from typing import Type

from rest_framework import viewsets, views, response, serializers, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from geo.models import AdminRegion, Tract, County, CountySubdivision, \
    BlockGroup, ZipCodeTabulationArea, Neighborhood
from geo.serializers import AdminRegionPolymorphicSerializer, \
    AdminRegionBriefSerializer, AdminRegionSerializer
from geo.util import all_geogs_in_extent
from indicators.utils import is_geog_data_request, get_geog_from_request


class GetGeog(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if is_geog_data_request(request):
            geog = get_geog_from_request(request)
            data = AdminRegionPolymorphicSerializer(geog).data
            return response.Response(data)
        return response.Response()


class GeoLevelView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        results = []
        for admin_region in [Tract, CountySubdivision, County, Neighborhood, BlockGroup, ZipCodeTabulationArea]:
            results.append({
                'id': admin_region.geog_type_id,
                'slug': admin_region.geog_type_slug,
                'name': admin_region.geog_type_title,
                'description': admin_region.type_description,
            })

        return Response(results)


class AdminRegionViewSet(viewsets.ReadOnlyModelViewSet):
    model: Type['AdminRegion'] = AdminRegion
    brief_serializer_class: [serializers.Serializer] = AdminRegionBriefSerializer
    detailed_serializer_class: [serializers.Serializer] = AdminRegionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'global_geoid']
    lookup_field = 'slug'

    def get_queryset(self):
        return all_geogs_in_extent(self.model)

    def get_serializer_class(self):
        if self.request.query_params.get('details'):
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
