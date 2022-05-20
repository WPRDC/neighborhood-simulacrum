from functools import lru_cache

from rest_framework import serializers

from context.serializers import TagSerializer, ContextItemSerializer
from geo.models import AdminRegion
from geo.serializers import AdminRegionPolymorphicSerializer
from . import TimeAxisPolymorphicSerializer
from .source import SourceSerializer
from .variable import VizVariablePolymorphicSerializer
from ..models.viz import DataViz
from ..utils import DataResponse


class DataVizBriefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataViz
        fields = (
            'id',
            'name',
            'slug',
            'viz_type',
            'description',
        )


class DataVizSerializer(serializers.HyperlinkedModelSerializer):
    variables = VizVariablePolymorphicSerializer(many=True)
    time_axis = TimeAxisPolymorphicSerializer()
    sources = SourceSerializer(many=True)
    static_options = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)

    class Meta:
        model = DataViz
        fields = (
            'id',
            'name',
            'slug',
            'viz_type',
            'description',
            'static_options',
            'sources',
            'time_axis',
            'variables',
            'tags',
            'context',
        )

    def get_static_options(self, obj: DataViz):
        return obj.options


class DataVizWithDataSerializer(DataVizSerializer):
    data = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()
    error = serializers.SerializerMethodField()
    warnings = serializers.SerializerMethodField()
    geogs = serializers.SerializerMethodField()

    _cached_response = None

    class Meta:
        model = DataViz
        fields = DataVizSerializer.Meta.fields + ('data', 'options', 'error', 'warnings', 'geogs')

    @lru_cache
    def _get_data_response(self, viz: DataViz, geog: AdminRegion) -> DataResponse:
        if self._cached_response:
            return self._cached_response
        return viz.get_viz_data(geog)

    def get_data(self, obj: DataViz):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(obj, self.context['geography'])
        if data_response.data:
            return [datum.as_dict() for datum in data_response.data]
        return None

    def get_options(self, obj: DataViz):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(obj, self.context['geography'])
        return data_response.options

    def get_error(self, obj: DataViz):
        if 'error' in self.context:
            return self.context['error']
        return self._get_data_response(obj, self.context['geography']).error.as_dict()

    def get_warnings(self, obj: DataViz):
        if 'error' in self.context:
            return self.context['warnings']
        warnings = self._get_data_response(obj, self.context['geography']).warnings
        if warnings:
            return [warning.as_dict() for warning in warnings]
        return None

    def get_geogs(self, obj: DataViz):
        return [AdminRegionPolymorphicSerializer(self.context['geography']).data]


class DataVizIdentifiersSerializer(serializers.HyperlinkedModelSerializer):
    """ Bare minimum info necessary for structuring site. """
    sources = SourceSerializer(many=True)

    class Meta:
        model = DataViz
        fields = (
            'id',
            'name',
            'slug',
            'viz_type',
            'sources',
        )
