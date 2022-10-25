from functools import lru_cache
from typing import Type

from rest_framework import serializers

from context.serializers import TagSerializer, ContextItemSerializer
from geo.models import AdminRegion
from geo.serializers import AdminRegionPolymorphicSerializer
from geo.util import all_geogs_in_extent
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


class IndicatorWithOptionsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Indicator
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'options',
        )


class IndicatorSerializer(serializers.HyperlinkedModelSerializer):
    variables = serializers.SerializerMethodField()
    time_axis = TimeAxisPolymorphicSerializer()
    sources = SourceSerializer(many=True)
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)

    class Meta:
        model = Indicator
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'tags',
            'context',
            # axes
            'time_axis',
            'variables',

            # properties
            'sources',
            'options',
        )

    def get_variables(self, obj: Indicator):
        print('indicator', obj.variables)
        return IndicatorVariablePolymorphicSerializer(
            obj.variables,
            context={'indicator': obj},
            many=True,
        ).data


class IndicatorWithDataSerializer(IndicatorSerializer):
    # the type of request made - indicates what data to expect (single, multi)
    request_type = serializers.SerializerMethodField()
    # 3d array of data records
    data = serializers.SerializerMethodField()
    # object with keys for each dimension pointing to an array of dimension points
    dimensions = serializers.SerializerMethodField()
    # props for wprdc-components/map and/or react-map-gl maps
    map_options = serializers.SerializerMethodField()
    # error record
    error = serializers.SerializerMethodField()
    # records for warnings
    warnings = serializers.SerializerMethodField()
    # brief details in geographies being examined
    geogs = serializers.SerializerMethodField()

    _cached_response = None

    class Meta:
        model = Indicator
        fields = IndicatorSerializer.Meta.fields + (
            'request_type',
            'data',
            'dimensions',
            'map_options',
            'error',
            'warnings',
            'geogs'
        )

    @lru_cache
    def _get_data_response(self, indicator: Indicator, geog: AdminRegion, across_geogs: bool) -> DataResponse:
        if self._cached_response:
            return self._cached_response
        return indicator.get_data(geog, across_geogs)

    def get_request_type(self, obj: Indicator):
        if 'error' in self.context:
            return ''
        if self.context.get('across_geogs', False):
            return 'multi-geog'
        return 'single-geog'

    def get_data(self, obj: Indicator):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(
            obj,
            self.context['geography'],
            across_geogs=self.context.get('across_geogs', False)
        )
        return data_response.data

    def get_dimensions(self, obj: Indicator):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(
            obj, self.context['geography'],
            across_geogs=self.context.get('across_geogs', False)
        )
        return data_response.dimensions.response_dict

    def get_map_options(self, obj: Indicator):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(
            obj,
            self.context['geography'],
            across_geogs=self.context.get('across_geogs', False)
        )
        return data_response.map_options

    def get_error(self, obj: Indicator):
        if 'error' in self.context:
            return self.context['error']
        return self._get_data_response(
            obj,
            self.context['geography'],
            across_geogs=self.context.get('across_geogs', False)
        ).error.as_dict()

    def get_warnings(self, obj: Indicator):
        if 'error' in self.context:
            return self.context['warnings']
        warnings = self._get_data_response(
            obj,
            self.context['geography'],
            across_geogs=self.context.get('across_geogs', False)
        ).warnings
        if warnings:
            return [warning.as_dict() for warning in warnings]
        return None

    def get_geogs(self, obj: Indicator):
        geog_type: Type['AdminRegion'] = type(self.context['geography'])
        if self.context.get('across_geogs'):
            all_geogs = all_geogs_in_extent(geog_type)
            return AdminRegionPolymorphicSerializer(all_geogs, many=True).data
        return [AdminRegionPolymorphicSerializer(self.context['geography']).data]
