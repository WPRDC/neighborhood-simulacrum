from typing import Optional, TYPE_CHECKING

from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import CensusGeography, CountySubdivision, Tract, BlockGroup, County, Neighborhood, ZipCodeTabulationArea

if TYPE_CHECKING:
    from indicators.models.variable import Datum


class CensusGeographyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusGeography
        fields = (
            'id',
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
            'title',
            'geog_type',
            'geogID',
            'hierarchy',
            'population',
            'kid_population',
            'black_population',
        )


class CensusGeographyDataMapSerializer(gis_serializers.GeoFeatureModelSerializer):
    """ Generates GeoJSON with dataviz data for a variable."""
    map_value = serializers.SerializerMethodField()
    locale_options = serializers.SerializerMethodField()

    class Meta:
        model = CensusGeography
        geo_field = 'geom'
        fields = (
            'id',
            'title',
            'geom',
            'map_value',
            'locale_options'
        )

    def get_map_value(self, obj: CensusGeography) -> Optional[float]:
        """ Gets value for a variable at a time for each feature """
        geoid = obj.common_geoid
        data: dict = {datum.geog: datum for datum in self.context.get('data', None)}
        use_percent = self.context.get('percent', False)
        if not data:
            return None
        datum: Optional['Datum'] = data.get(geoid, None)
        if use_percent:
            return datum.percent if datum else None
        return datum.value if datum else None

    def get_locale_options(self, obj: CensusGeography) -> Optional[float]:
        return self.context.get('locale_options', {})


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
