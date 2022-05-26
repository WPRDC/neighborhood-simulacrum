from rest_framework import serializers

from context.serializers import TagSerializer, ContextItemSerializer
from indicators.models import Domain, Subdomain, Topic, Taxonomy, TopicIndicator
from .indicator import IndicatorSerializer, IndicatorWithDataSerializer, IndicatorBriefSerializer
from .source import CensusSourceSerializer, CKANSourceSerializer, CKANRegionalSourceSerializer, CKANGeomSourceSerializer
from .time import TimeAxisPolymorphicSerializer, StaticTimeAxisSerializer, TimeAxisSerializer
from .variable import VariablePolymorphicSerializer, CensusVariableSerializer, CKANVariableSerializer


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


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    indicators = IndicatorBriefSerializer(many=True)
    hierarchies = HierarchySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)
    primary_indicatorIDs = serializers.SerializerMethodField()
    child_tags = TagSerializer(many=True)

    class Meta:
        model = Topic
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'tags',
            'child_tags',
            'context',
            # details
            'long_description',
            'full_description',
            'limitations',
            'importance',
            'source',
            'provenance',
            # relations
            'indicators',
            'hierarchies',
            'primary_indicatorIDs',
        )
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }

    def get_primary_indicatorIDs(self, obj: Topic):
        primary_indicators = TopicIndicator.objects.filter(topic=obj, primary=True)
        return [v.id for v in primary_indicators]


class SubdomainSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True)
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)

    class Meta:
        model = Subdomain
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'topics',
            'tags',
            'context',
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
            'tags',
            'context',
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
            'domains',
            'tags',
            'context',
        )
