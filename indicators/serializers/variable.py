from typing import TYPE_CHECKING, Dict

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from indicators.models import Variable, CensusVariable, CKANVariable, CensusVariableSource, VizVariable, DataViz
from indicators.serializers import CKANSourceSerializer

if TYPE_CHECKING:
    from indicators.views import DataVizViewSet


def get_dataviz_from_view(view: 'DataVizViewSet'):
    data_viz_id = view.kwargs.get(view.lookup_field)
    return DataViz.objects.get(pk=data_viz_id)


class DenominatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variable
        fields = (
            'id',
            'name',
            'slug',
            'depth',
            'percent_label',
            'short_name',
            'locale_options'
        )


class VariableSerializer(serializers.ModelSerializer):
    denominators = DenominatorSerializer(many=True)
    locale_options = serializers.JSONField()

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
            'depth',
            'display_name',
            'percent_label',
            'locale_options',
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
    viz_options = serializers.JSONField()

    class Meta:
        model = CensusVariable
        fields = VariableSerializer.Meta.fields + (
            'sources',
            'viz_options',
        )


class CKANVariableSerializer(VariableSerializer):
    sources = CKANSourceSerializer(many=True)
    viz_options = serializers.JSONField()

    class Meta:
        model = CKANVariable
        fields = VariableSerializer.Meta.fields + (
            'sources',
            'viz_options'
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
    options = serializers.SerializerMethodField()

    class Meta:
        model = CensusVariable
        fields = VariableSerializer.Meta.fields + ('sources', 'options')

    def get_options(self, obj: 'CensusVariable') -> Dict:
        data_viz: DataViz = get_dataviz_from_view(self.context['view'])
        return obj.get_options_for_dataviz(data_viz)


class CKANVizVariableSerializer(VariableSerializer):
    denominators = DenominatorSerializer(many=True)
    options = serializers.SerializerMethodField()

    class Meta:
        model = CKANVariable
        fields = VariableSerializer.Meta.fields + ('sources', 'options')

    def get_options(self, obj: 'CKANVariable'):
        return obj.get_options()


class VizVariablePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        CensusVariable: CensusVizVariableSerializer,
        CKANVariable: CKANVizVariableSerializer,
    }
