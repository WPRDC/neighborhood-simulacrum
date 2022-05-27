from functools import lru_cache

from rest_framework import serializers

from context.serializers import TagSerializer, ContextItemSerializer
from geo.models import AdminRegion
from geo.serializers import AdminRegionPolymorphicSerializer
from .time import TimeAxisPolymorphicSerializer
from .source import SourceSerializer
from .variable import IndicatorVariablePolymorphicSerializer
from ..models.indicator import Indicator
from ..utils import DataResponse


class IndicatorBriefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Indicator
        fields = (
            'id',
            'name',
            'slug',
            'description',
        )


class IndicatorSerializer(serializers.HyperlinkedModelSerializer):
    variables = IndicatorVariablePolymorphicSerializer(many=True)
    time_axis = TimeAxisPolymorphicSerializer()
    sources = SourceSerializer(many=True)
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)
    child_tags = TagSerializer(many=True)

    class Meta:
        model = Indicator
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'tags',
            'child_tags',
            'context',
            # axes
            'time_axis',
            'variables',

            # properties
            'sources',
            'options',
            'multidimensional',
        )


class IndicatorWithDataSerializer(IndicatorSerializer):
    data = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()
    map_options = serializers.SerializerMethodField()
    error = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()
    geogs = serializers.SerializerMethodField()

    _cached_response = None

    class Meta:
        model = Indicator
        fields = IndicatorSerializer.Meta.fields + ('data', 'dimensions', 'map_options', 'error', 'warnings', 'geogs')

    @lru_cache
    def _get_data_response(self, indicator: Indicator, geog: AdminRegion) -> DataResponse:
        if self._cached_response:
            return self._cached_response
        return indicator.get_data(geog)

    def get_data(self, obj: Indicator):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(obj, self.context['geography'])
        if data_response.data:
            return [datum.as_dict() for datum in data_response.data]
        return None

    def get_dimensions(self, obj: Indicator):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(obj, self.context['geography'])
        return data_response.dimensions

    def get_map_options(self, obj: Indicator):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(obj, self.context['geography'])
        return data_response.map_options

    def get_error(self, obj: Indicator):
        if 'error' in self.context:
            return self.context['error']
        return self._get_data_response(obj, self.context['geography']).error.as_dict()

    def get_warnings(self, obj: Indicator):
        if 'error' in self.context:
            return self.context['warnings']
        warnings = self._get_data_response(obj, self.context['geography']).warnings
        if warnings:
            return [warning.as_dict() for warning in warnings]
        return None

    def get_geogs(self, obj: Indicator):
        return [AdminRegionPolymorphicSerializer(self.context['geography']).data]
