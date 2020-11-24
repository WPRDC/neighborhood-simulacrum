from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from . import SeriesPolymorphicSerializer
from .variable import BriefVariablePolymorphicSerializer
from ..models import DataViz, Table


class DataVizSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataViz
        fields = (
            'id',
            'name',
            'slug',
            'series',
            'variables',
            'indicator',
        )


class TableSerializer(serializers.HyperlinkedModelSerializer):
    variables = BriefVariablePolymorphicSerializer(many=True)
    series = SeriesPolymorphicSerializer(many=True)

    class Meta:
        model = Table
        fields = (
            'id',
            'name',
            'slug',
            'series',
            'variables',
            'indicator',
        )


class DataVizPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        DataViz: DataVizSerializer,
        Table: TableSerializer,
    }


# ---
# with data

class DataVizWithDataSerializer(serializers.HyperlinkedModelSerializer):
    variables = BriefVariablePolymorphicSerializer(many=True)
    series = SeriesPolymorphicSerializer(many=True)

    class Meta:
        model = DataViz
        fields = (
            'id',
            'name',
            'slug',
            'series',
            'variables',
            'indicator',
        )


class TableWithDataSerializer(serializers.HyperlinkedModelSerializer):
    variables = BriefVariablePolymorphicSerializer(many=True)
    series = SeriesPolymorphicSerializer(many=True)

    data = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = (
            'id',
            'name',
            'slug',
            'series',
            'variables',
            'indicator',
            'data',
        )

    def get_data(self, obj: Table):
        return obj.get_table_data(self.context['region'])


class DataVizWithDataPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        DataViz: DataVizWithDataSerializer,
        Table: TableWithDataSerializer,
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


class TableIdentifiersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Table
        fields = (
            'id',
            'name',
            'slug',
        )


class DataVizIdentifiersPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        DataViz: DataVizIdentifiersSerializer,
        Table: TableIdentifiersSerializer,
    }
