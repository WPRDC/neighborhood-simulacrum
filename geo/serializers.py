from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import CensusGeography, CountySubdivision, Tract, BlockGroup, County


class CensusGeographyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusGeography
        fields = (
            'id',
            'title',
            'geog_type',
            'geogID'
        )


class CensusGeographySerializer(serializers.ModelSerializer):
    hierarchy = CensusGeographyBriefSerializer(many=True)

    class Meta:
        model = CensusGeography
        fields = (
            'id',
            'title',
            'geog_type',
            'geogID',
            'hierarchy',
            'population',
            'kid_population',
        )


class CensusGeographyDataMapSerializer(gis_serializers.GeoFeatureModelSerializer):
    """ Generates GeoJSON with dataviz data for a variable."""
    map_value = serializers.SerializerMethodField()

    class Meta:
        model = CensusGeography
        geo_field = 'geom'
        fields = (
            'id',
            'title',
            'geom',
            'map_value',
        )

    def get_map_value(self, obj: CensusGeography):
        """ Gets value for a variable at a time for each feature """
        data: dict = self.context.get('data', None)
        geoid = obj.common_geoid
        if not data:
            return None
        return data.get(geoid, None)


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
