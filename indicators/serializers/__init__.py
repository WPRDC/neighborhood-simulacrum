from rest_framework import serializers

from indicators.models import Domain, Subdomain, Indicator, Taxonomy
from .time import TimeAxisPolymorphicSerializer, StaticTimeAxisSerializer, TimeAxisSerializer
from .source import CensusSourceSerializer, CKANSourceSerializer, CKANRegionalSourceSerializer, CKANGeomSourceSerializer
from .variable import VariablePolymorphicSerializer, CensusVariableSerializer, CKANVariableSerializer
from .viz import DataVizSerializer, DataVizWithDataSerializer, DataVizIdentifiersSerializer, DataVizBriefSerializer


class TaxonomyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxonomy
        fields = ('id', 'slug', 'name')


class DomainBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ('id', 'slug', 'name')


class SubdomainBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ('id', 'slug', 'name')


class HierarchySerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    domain = DomainBriefSerializer(read_only=True)
    subdomain = SubdomainBriefSerializer(read_only=True)


class IndicatorSerializer(serializers.HyperlinkedModelSerializer):
    data_vizes = DataVizIdentifiersSerializer(many=True)
    hierarchies = HierarchySerializer(many=True, read_only=True)

    class Meta:
        model = Indicator
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'long_description',
            'full_description',
            'limitations',
            'importance',
            'source',
            'provenance',
            'data_vizes',
            'hierarchies',
        )
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class SubdomainSerializer(serializers.ModelSerializer):
    indicators = IndicatorSerializer(many=True)

    class Meta:
        model = Subdomain
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'indicators',
        )


class DomainSerializer(serializers.ModelSerializer):
    subdomains = SubdomainSerializer(many=True)

    class Meta:
        model = Domain
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'subdomains',
        )


class TaxonomySerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True)

    class Meta:
        model = Taxonomy
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'domains'
        )
