from typing import TYPE_CHECKING

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from context.serializers import TagSerializer, ContextItemSerializer
from indicators.models import Variable, CensusVariable, CKANVariable, CensusVariableSource
from indicators.serializers.source import CKANSourceSerializer

if TYPE_CHECKING:
    pass


class DenominatorSerializer(serializers.ModelSerializer):
    locale_options = serializers.JSONField()
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)

    class Meta:
        model = Variable
        fields = (
            'id',
            'name',
            'slug',
            'depth',
            'percent_label',
            'short_name',
            'locale_options',
            'tags',
            'context',
        )


class VariableSerializer(serializers.ModelSerializer):
    denominators = DenominatorSerializer(many=True)
    locale_options = serializers.JSONField()
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)

    class Meta:
        model = Variable
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'short_name',
            'units',
            'unit_notes',
            'denominators',
            'sources',
            'depth',
            'display_name',
            'percent_label',
            'locale_options',
            'tags',
            'context',
        )


class CensusVariableSourceSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='source.name')
    slug = serializers.ReadOnlyField(source='source.slug')
    description = serializers.ReadOnlyField(source='source.description')
    dataset = serializers.ReadOnlyField(source='source.dataset')
    info_link = serializers.ReadOnlyField(source='source.info_link')

    class Meta:
        model = CensusVariableSource
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'dataset',
            'info_link',
        )


class CensusVariableSerializer(VariableSerializer):
    sources = CensusVariableSourceSerializer(source='variable_to_source', many=True)

    class Meta:
        model = CensusVariable
        fields = VariableSerializer.Meta.fields + (
            'sources',
        )


class CKANVariableSerializer(VariableSerializer):
    sources = CKANSourceSerializer(many=True)

    class Meta:
        model = CKANVariable
        fields = VariableSerializer.Meta.fields + (
            'sources',
        )


class VariablePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        CensusVariable: CensusVariableSerializer,
        CKANVariable: CKANVariableSerializer,
    }


# Brief
class CensusVariableBriefSerializer(VariableSerializer):
    sources = CensusVariableSourceSerializer(source='variable_to_source', many=True)
    denominators = DenominatorSerializer(many=True)

    class Meta:
        model = CensusVariable
        fields = VariableSerializer.Meta.fields + ('sources',)


class CKANVariableBriefSerializer(serializers.ModelSerializer):
    sources = CKANSourceSerializer(many=True)
    denominators = DenominatorSerializer(many=True)

    class Meta:
        model = CKANVariable
        fields = VariableSerializer.Meta.fields + ('sources',)


class BriefVariablePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        CensusVariable: CensusVariableBriefSerializer,
        CKANVariable: CKANVariableBriefSerializer,
    }


# With Viz
class CensusVizVariableSerializer(VariableSerializer):
    denominators = DenominatorSerializer(many=True)

    class Meta:
        model = CensusVariable
        fields = VariableSerializer.Meta.fields + ('sources',)


class CKANVizVariableSerializer(VariableSerializer):
    denominators = DenominatorSerializer(many=True)

    class Meta:
        model = CKANVariable
        fields = VariableSerializer.Meta.fields + ('sources', )


class VizVariablePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        CensusVariable: CensusVizVariableSerializer,
        CKANVariable: CKANVizVariableSerializer,
    }
