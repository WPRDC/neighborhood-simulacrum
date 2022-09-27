from django.shortcuts import render
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from parcels.models import Parcel
from parcels.serializers import ParcelBriefSerializer, ParcelSerializer


class ParcelViewSet(viewsets.ModelViewSet):
    queryset = Parcel.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['parcel_id', '']

    def get_serializer_class(self):
        if self.action == 'list':
            return ParcelBriefSerializer
        return ParcelSerializer
