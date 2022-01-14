from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import (
    AdminRegion,
    CountySubdivision,
    Tract,
    BlockGroup,
    County,
    Neighborhood,
    ZipCodeTabulationArea
)


class AdminRegionBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminRegion
        fields = (
            'id',
            'name',
            'slug',
            'title',
            'geog_type',
            'geogID',
        )


class AdminRegionSerializer(serializers.ModelSerializer):
    hierarchy = AdminRegionBriefSerializer(many=True)

    class Meta:
        model = AdminRegion
        fields = (
            'id',
            'name',
            'title',
            'geog_type',
            'geogID',
            'hierarchy',
        )


class CountySerializer(AdminRegionSerializer):
    class Meta:
        model = County
        fields = AdminRegionSerializer.Meta.fields


class CountySubdivisionSerializer(AdminRegionSerializer):
    class Meta:
        model = CountySubdivision
        fields = AdminRegionSerializer.Meta.fields


class TractSerializer(AdminRegionSerializer):
    class Meta:
        model = Tract
        fields = AdminRegionSerializer.Meta.fields


class BlockGroupSerializer(AdminRegionSerializer):
    class Meta:
        model = BlockGroup
        fields = AdminRegionSerializer.Meta.fields


class NeighborhoodSerializer(AdminRegionSerializer):
    class Meta:
        model = Neighborhood
        fields = AdminRegionSerializer.Meta.fields


class ZipCodeTabulationAreaSerializer(AdminRegionSerializer):
    class Meta:
        model = ZipCodeTabulationArea
        fields = AdminRegionSerializer.Meta.fields


class AdminRegionPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        County: CountySerializer,
        Tract: TractSerializer,
        CountySubdivision: CountySubdivisionSerializer,
        BlockGroup: BlockGroupSerializer,
        Neighborhood: NeighborhoodSerializer,
        ZipCodeTabulationArea: ZipCodeTabulationAreaSerializer,
    }
