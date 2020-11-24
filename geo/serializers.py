from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import CensusGeography, CountySubdivision, Tract, BlockGroup, County


class HierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusGeography
        fields = (
            'id',
            'title'
        )


class CensusGeographySerializer(serializers.ModelSerializer):
    hierarchy = HierarchySerializer(many=True)

    class Meta:
        model = CensusGeography
        fields = (
            'id',
            'title',
            'hierarchy',
        )


class CountySerializer(serializers.ModelSerializer):
    hierarchy = HierarchySerializer(many=True)

    class Meta:
        model = County
        fields = (
            'id',
            'title',
            'hierarchy',
        )


class CountySubdivisionSerializer(serializers.ModelSerializer):
    hierarchy = HierarchySerializer(many=True)

    class Meta:
        model = CountySubdivision
        fields = (
            'id',
            'title',
            'hierarchy',
        )


class TractSerializer(serializers.ModelSerializer):
    hierarchy = HierarchySerializer(many=True)

    class Meta:
        model = Tract
        fields = (
            'id',
            'title',
            'hierarchy',
        )


class BlockGroupSerializer(serializers.ModelSerializer):
    hierarchy = HierarchySerializer(many=True)

    class Meta:
        model = BlockGroup
        fields = (
            'id',
            'title',
            'hierarchy',
        )


class CensusGeographyPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        CensusGeography: CensusGeographySerializer,
        County: CountySerializer,
        Tract: TractSerializer,
        CountySubdivision: CountySubdivisionSerializer,
        BlockGroup: BlockGroupSerializer
    }
