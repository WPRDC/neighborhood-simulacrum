from rest_framework import serializers

from context.serializers import TagSerializer, ContextItemSerializer
from indicators.models import Domain, Topic, Taxonomy, TopicIndicator
from .indicator import IndicatorSerializer, IndicatorWithDataSerializer, IndicatorBriefSerializer, \
    IndicatorWithOptionsSerializer
from .source import CensusSourceSerializer, CKANSourceSerializer, CKANRegionalSourceSerializer, CKANGeomSourceSerializer
from .time import TimeAxisPolymorphicSerializer, StaticTimeAxisSerializer, TimeAxisSerializer
from .variable import VariablePolymorphicSerializer, CensusVariableSerializer, CKANVariableSerializer


class DomainBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ('id', 'slug', 'name')


class HierarchySerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    domain = DomainBriefSerializer(read_only=True)


class TopicBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ('id', 'slug', 'name', 'description')


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    indicators = IndicatorWithOptionsSerializer(many=True)
    hierarchies = HierarchySerializer(many=True, read_only=True)
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
        primary_indicators = TopicIndicator.objects.filter(topic=obj, primary=True)
        return [v.id for v in primary_indicators]


class DomainSerializer(serializers.ModelSerializer):
    topics = TopicBriefSerializer(many=True)

    class Meta:
        model = Domain
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
