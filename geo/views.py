from django.http import JsonResponse
from rest_framework import viewsets, views, response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geo.models import CensusGeography
from geo.serializers import CensusGeographyPolymorphicSerializer
from indicators.utils import is_region_data_request, get_region_from_query_params


class CensusGeographyViewSet(viewsets.ModelViewSet):
    queryset = CensusGeography.objects.all()
    serializer_class = CensusGeographyPolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if is_region_data_request(self.request):
            region = get_region_from_query_params(self.request)
            return CensusGeography.objects.filter(pk=region.pk)
        return self.queryset


class GetRegion(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        if is_region_data_request(request):
            region = get_region_from_query_params(request)
            data = CensusGeographyPolymorphicSerializer(region).data
            return response.Response(data)
        return response.Response()