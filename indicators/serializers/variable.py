from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from indicators.models import Variable, CensusVariable, CKANVariable, CensusVariableSource


class DenominatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variable
        fields = (
            'id',
            'name',
            'slug',
            'depth',
            'percent_label',
        )


class CensusVariableSourceSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='source.name')
    slug = serializers.ReadOnlyField(source='source.slug')
    description = serializers.ReadOnlyField(source='source.description')
    dataset = serializers.ReadOnlyField(source='source.dataset')

    class Meta:
        model = CensusVariableSource
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'dataset',
            'formula'
        )


class CensusVariableSerializer(serializers.ModelSerializer):
    sources = CensusVariableSourceSerializer(source='variable_to_source', many=True)

    class Meta:
        model = CensusVariable
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'units',
            'unit_notes',
            'denominators',
            'depth',
            'percent_label',
            'sources',
        )


class CensusVariableBriefSerializer(serializers.ModelSerializer):
    sources = CensusVariableSourceSerializer(source='variable_to_source', many=True)
    denominators = DenominatorSerializer(many=True)

    class Meta:
        model = CensusVariable
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'units',
            'unit_notes',
            'depth',
            'percent_label',
            'sources',
            'denominators',
        )


class CKANVariableSerializer(serializers.ModelSerializer):
    denominators = DenominatorSerializer(many=True)

    class Meta:
        model = CKANVariable
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'units',
            'unit_notes',
            'denominators',
            'depth',
            'percent_label',
            'sources',
            'aggregation_method',
            'field',
            'sql_filter'
        )


class CKANVariableBriefSerializer(serializers.ModelSerializer):
    denominators = DenominatorSerializer(many=True)

    class Meta:
        model = CKANVariable
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'units',
            'unit_notes',
            'denominators',
            'depth',
            'percent_label',
            'sources',
            'aggregation_method',
            'field',
            'sql_filter'
        )


class VariablePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        CensusVariable: CensusVariableSerializer,
        CKANVariable: CKANVariableSerializer,
    }


class BriefVariablePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        CensusVariable: CensusVariableBriefSerializer,
        CKANVariable: CKANVariableBriefSerializer,
    }
