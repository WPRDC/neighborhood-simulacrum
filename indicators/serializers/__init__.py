from rest_framework import serializers

from context.serializers import TagSerializer, ContextItemSerializer
from indicators.models import Domain, Topic, Taxonomy, TopicIndicator, Subdomain
from profiles.abstract_models import Described
from .indicator import IndicatorSerializer, IndicatorWithDataSerializer, IndicatorBriefSerializer, \
    IndicatorWithOptionsSerializer
from .source import CensusSourceSerializer, CKANSourceSerializer, CKANRegionalSourceSerializer, CKANGeomSourceSerializer
from .time import TimeAxisPolymorphicSerializer, StaticTimeAxisSerializer, TimeAxisSerializer
from .variable import VariablePolymorphicSerializer, CensusVariableSerializer, CKANVariableSerializer


class DomainBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ('id', 'slug', 'name')


class SubdomainBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subdomain
        fields = ('id', 'slug', 'name')


class HierarchyListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        pass


class HierarchySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=200)
    slug = serializers.CharField(max_length=200)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        list_serializer_class = HierarchyListSerializer


class TopicBriefSerializer(serializers.ModelSerializer):
    hierarchies = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = ('id', 'slug', 'name', 'description', 'hierarchies',)

    def get_hierarchies(self, obj: Topic):
        hierarchies = [HierarchySerializer(item, many=True).data for item in obj.hierarchies]
        serialized = {
            item[0]['slug']: item[1:] for item in hierarchies
        }
        return serialized


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    indicators = IndicatorWithOptionsSerializer(many=True)
    hierarchies = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)
    primary_indicatorIDs = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'tags',
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
        primary_topic_indicators = TopicIndicator.objects.filter(topic=obj, primary=True)
        primary_indicators = [ti.indicator for ti in primary_topic_indicators]
        return [v.id for v in primary_indicators]

    def get_hierarchies(self, obj: Topic):
        hierarchies = [HierarchySerializer(item, many=True).data for item in obj.hierarchies]
        serialized = {
            item[0]['slug']: item[1:] for item in hierarchies
        }
        return serialized


class DomainSerializer(serializers.ModelSerializer):
    subdomains = serializers.SerializerMethodField()

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

    def get_subdomains(self, obj: Domain):
        return SubdomainBriefSerializer(obj.ordered_subdomains, many=True).data


class SubdomainSerializer(serializers.ModelSerializer):
    topics = TopicBriefSerializer(many=True)

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


class TaxonomySerializer(serializers.ModelSerializer):
    domains = DomainBriefSerializer(many=True)

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


class TaxonomyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxonomy
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'tags',
        )
