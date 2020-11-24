from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from indicators.models import YearSeries, Series


class SeriesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Series
        fields = (
            'id',
            'name',
            'slug',
            'description',
        )


class YearSeriesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = YearSeries
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'year',
        )


class SeriesPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Series: SeriesSerializer,
        YearSeries: YearSeriesSerializer,
    }
