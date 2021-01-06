from functools import lru_cache

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from geo.models import CensusGeography
from . import TimeAxisPolymorphicSerializer
from .variable import BriefVariablePolymorphicSerializer
from ..models import DataViz, Table
from ..models.viz import BarChart, PopulationPyramidChart, PieChart, LineChart, BigValue, Sentence
from ..utils import DataResponse


class DataVizSerializer(serializers.HyperlinkedModelSerializer):
    variables = BriefVariablePolymorphicSerializer(many=True)
    time_axis = TimeAxisPolymorphicSerializer()

    class Meta:
        model = DataViz
        fields = (
            'id',
            'name',
            'slug',
            'time_axis',
            'variables',
            'indicator',
        )


class TableSerializer(DataVizSerializer):
    class Meta:
        model = Table
        fields = DataVizSerializer.Meta.fields + (
            'transpose',
        )


class BarChartSerializer(DataVizSerializer):
    class Meta:
        model = BarChart
        fields = DataVizSerializer.Meta.fields + (
            'layout',
        )


class BigValueSerializer(DataVizSerializer):
    class Meta:
        model = BigValue
        fields = DataVizSerializer.Meta.fields + (
            'note',
        )


class SentenceSerializer(DataVizSerializer):
    class Meta:
        model = Sentence
        fields = DataVizSerializer.Meta.fields + (
            'text',
        )


class LineChartSerializer(DataVizSerializer):
    class Meta(DataVizSerializer.Meta):
        model = LineChart


class PieChartSerializer(DataVizSerializer):
    class Meta(DataVizSerializer.Meta):
        model = PieChart


class PopulationPyramidChartSerializer(DataVizSerializer):
    class Meta(DataVizSerializer.Meta):
        model = PopulationPyramidChart


class DataVizPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Table: TableSerializer,
        BarChart: BarChartSerializer,
        BigValue: BigValueSerializer,
        Sentence: SentenceSerializer,
        LineChart: LineChartSerializer,
        PieChart: PieChartSerializer,
        PopulationPyramidChart: PopulationPyramidChartSerializer,
    }


# ---
# with data

class WithData(serializers.Serializer):
    data = serializers.SerializerMethodField()
    error = serializers.SerializerMethodField()

    class Meta:
        fields = ('data', 'error')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass

    @lru_cache
    def _get_data_response(self, viz: DataViz, geog: CensusGeography) -> DataResponse:
        return viz.get_viz_data(geog)

    def get_data(self, obj: DataViz):
        if 'error' in self.context:
            return []
        return self._get_data_response(obj, self.context['geography']).data

    def get_error(self, obj: DataViz):
        if 'error' in self.context:
            return self.context['error']
        return self._get_data_response(obj, self.context['geography']).error.as_dict()


class TableWithDataSerializer(TableSerializer, WithData):
    class Meta:
        model = Table
        fields = TableSerializer.Meta.fields + WithData.Meta.fields


class BarChartWithDataSerializer(BarChartSerializer, WithData):
    class Meta:
        model = BarChart
        fields = BarChartSerializer.Meta.fields + WithData.Meta.fields


class BigValueWithDataSerializer(BigValueSerializer, WithData):
    class Meta:
        model = BigValue
        fields = BigValueSerializer.Meta.fields + WithData.Meta.fields


class SentenceWithDataSerializer(SentenceSerializer, WithData):
    class Meta:
        model = Sentence
        fields = SentenceSerializer.Meta.fields + WithData.Meta.fields


class LineChartWithDataSerializer(LineChartSerializer, WithData):
    class Meta:
        model = LineChart
        fields = LineChartSerializer.Meta.fields + WithData.Meta.fields


class PieChartWithDataSerializer(PieChartSerializer, WithData):
    class Meta:
        model = PieChart
        fields = PieChartSerializer.Meta.fields + WithData.Meta.fields


class PopulationPyramidChartWithDataSerializer(PopulationPyramidChartSerializer, WithData):
    class Meta:
        model = PopulationPyramidChart
        fields = PopulationPyramidChartSerializer.Meta.fields + WithData.Meta.fields


class DataVizWithDataPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Table: TableWithDataSerializer,
        BarChart: BarChartWithDataSerializer,
        BigValue: BigValueWithDataSerializer,
        Sentence: SentenceWithDataSerializer,
        LineChart: LineChartWithDataSerializer,
        PieChart: PieChartWithDataSerializer,
        PopulationPyramidChart: PopulationPyramidChartWithDataSerializer,
    }


# ---
# brief

class DataVizIdentifiersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataViz
        fields = (
            'id',
            'name',
            'slug',
        )


class TableIdentifiersSerializer(DataVizIdentifiersSerializer):
    class Meta:
        model = Table
        fields = DataVizIdentifiersSerializer.Meta.fields


class BarChartIdentifiersSerializer(DataVizIdentifiersSerializer):
    class Meta:
        model = BarChart
        fields = DataVizIdentifiersSerializer.Meta.fields


class BigValueIdentifiersSerializer(DataVizIdentifiersSerializer):
    class Meta:
        model = BigValue
        fields = DataVizIdentifiersSerializer.Meta.fields


class SentenceIdentifiersSerializer(DataVizIdentifiersSerializer):
    class Meta:
        model = Sentence
        fields = DataVizIdentifiersSerializer.Meta.fields


class LineChartIdentifiersSerializer(DataVizIdentifiersSerializer):
    class Meta:
        model = LineChart
        fields = DataVizIdentifiersSerializer.Meta.fields


class PieChartIdentifiersSerializer(DataVizIdentifiersSerializer):
    class Meta:
        model = PieChart
        fields = DataVizIdentifiersSerializer.Meta.fields


class PopulationPyramidChartIdentifiersSerializer(DataVizIdentifiersSerializer):
    class Meta:
        model = PopulationPyramidChart
        fields = DataVizIdentifiersSerializer.Meta.fields


class DataVizIdentifiersPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Table: TableIdentifiersSerializer,
        BarChart: BarChartIdentifiersSerializer,
        BigValue: BigValueIdentifiersSerializer,
        Sentence: SentenceIdentifiersSerializer,
        LineChart: LineChartIdentifiersSerializer,
        PieChart: PieChartIdentifiersSerializer,
        PopulationPyramidChart: PopulationPyramidChartIdentifiersSerializer,
    }
