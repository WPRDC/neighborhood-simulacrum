from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import CensusGeography, CountySubdivision, Tract, BlockGroup, County


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusGeography
        fields = (
            'id',
            'title',
            'region_type',
            'regionID'
        )


class CensusGeographySerializer(serializers.ModelSerializer):
    hierarchy = HierarchySerializer(many=True)

    class Meta:
        model = CensusGeography
        fields = (
            'id',
            'title',
            'region_type',
            'regionID',
            'hierarchy',
            'population',
            'kid_population',
        )


class CountySerializer(CensusGeographySerializer):
    class Meta:
        model = County
        fields = CensusGeographySerializer.Meta.fields


class CountySubdivisionSerializer(CensusGeographySerializer):
    class Meta:
        model = CountySubdivision
        fields = CensusGeographySerializer.Meta.fields


class TractSerializer(CensusGeographySerializer):
    class Meta:
        model = Tract
        fields = CensusGeographySerializer.Meta.fields


class BlockGroupSerializer(CensusGeographySerializer):
    class Meta:
        model = BlockGroup
        fields = CensusGeographySerializer.Meta.fields


class CensusGeographyPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        County: CountySerializer,
        Tract: TractSerializer,
        CountySubdivision: CountySubdivisionSerializer,
        BlockGroup: BlockGroupSerializer
    }
