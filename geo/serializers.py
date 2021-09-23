from typing import TYPE_CHECKING

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import CensusGeography, CountySubdivision, Tract, BlockGroup, County, Neighborhood, ZipCodeTabulationArea


class CensusGeographyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusGeography
        fields = (
            'id',
            'name',
            'title',
            'geog_type',
            'geogID',
        )


class CensusGeographySerializer(serializers.ModelSerializer):
    hierarchy = CensusGeographyBriefSerializer(many=True)

    class Meta:
        model = CensusGeography
        fields = (
            'id',
            'name',
            'title',
            'geog_type',
            'geogID',
            'hierarchy',
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


class NeighborhoodSerializer(CensusGeographySerializer):
    class Meta:
        model = Neighborhood
        fields = CensusGeographySerializer.Meta.fields


class ZipCodeTabulationAreaSerializer(CensusGeographySerializer):
    class Meta:
        model = ZipCodeTabulationArea
        fields = CensusGeographySerializer.Meta.fields


class CensusGeographyPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        County: CountySerializer,
        Tract: TractSerializer,
        CountySubdivision: CountySubdivisionSerializer,
        BlockGroup: BlockGroupSerializer,
        Neighborhood: NeighborhoodSerializer,
        ZipCodeTabulationArea: ZipCodeTabulationAreaSerializer,
    }
