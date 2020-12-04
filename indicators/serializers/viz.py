from abc import ABC

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from . import TimeAxisPolymorphicSerializer
from .variable import BriefVariablePolymorphicSerializer
from ..models import DataViz, Table
from ..models.viz import BarChart, PopulationPyramidChart, PieChart, LineChart


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
        LineChart: LineChartSerializer,
        PieChart: PieChartSerializer,
        PopulationPyramidChart: PopulationPyramidChartSerializer,
    }


# ---
# with data
class WithData(serializers.Serializer):
    data = serializers.SerializerMethodField()


class TableWithDataSerializer(TableSerializer, WithData):
    class Meta:
        model = Table
        fields = TableSerializer.Meta.fields + ('data',)

    def get_data(self, obj: Table):
        return obj.get_table_data(self.context['region'])


class BarChartWithDataSerializer(BarChartSerializer, WithData):
    class Meta:
        model = BarChart
        fields = BarChartSerializer.Meta.fields + ('data',)

    def get_data(self, obj: BarChart):
        return obj.get_chart_data(self.context['region'])


class LineChartWithDataSerializer(LineChartSerializer, WithData):
    class Meta:
        model = LineChart
        fields = LineChartSerializer.Meta.fields + ('data',)

    def get_data(self, obj: LineChart):
        return obj.get_chart_data(self.context['region'])


class PieChartWithDataSerializer(PieChartSerializer, WithData):
    class Meta:
        model = PieChart
        fields = PieChartSerializer.Meta.fields + ('data',)

    def get_data(self, obj: PieChart):
        return obj.get_chart_data(self.context['region'])


class PopulationPyramidChartWithDataSerializer(PopulationPyramidChartSerializer, WithData):
    class Meta:
        model = PopulationPyramidChart
        fields = PopulationPyramidChartSerializer.Meta.fields + ('data',)

    def get_data(self, obj: PopulationPyramidChart):
        return obj.get_chart_data(self.context['region'])


class DataVizWithDataPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Table: TableWithDataSerializer,
        BarChart: BarChartWithDataSerializer,
        LineChart: LineChartWithDataSerializer,
        PieChart: PieChartWithDataSerializer,
        PopulationPyramidChart: PopulationPyramidChartWithDataSerializer, }


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
        LineChart: LineChartIdentifiersSerializer,
        PieChart: PieChartIdentifiersSerializer,
        PopulationPyramidChart: PopulationPyramidChartIdentifiersSerializer,
    }
