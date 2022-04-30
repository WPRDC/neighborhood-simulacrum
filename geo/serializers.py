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


class AdminRegionHierarchySerializer(serializers.ModelSerializer):
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


class AdminRegionBriefSerializer(serializers.ModelSerializer):
    centroid = serializers.SerializerMethodField()

    class Meta:
        model = AdminRegion
        fields = (
            'id',
            'name',
            'slug',
            'title',
            'geog_type',
            'geogID',
            'centroid',
        )

    def get_centroid(self, obj):
        return obj.centroid.coords


class AdminRegionSerializer(serializers.ModelSerializer):
    hierarchy = AdminRegionHierarchySerializer(many=True)
    centroid = serializers.SerializerMethodField()

    class Meta:
        model = AdminRegion
        fields = (
            'id',
            'name',
            'slug',
            'title',
            'geog_type',
            'geogID',
            'hierarchy',
            'overlap',
            'centroid'
        )

    def get_centroid(self, obj):
        return obj.centroid.coords


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
