from functools import lru_cache

from rest_framework import serializers

from geo.models import CensusGeography
from geo.serializers import CensusGeographyPolymorphicSerializer
from . import TimeAxisPolymorphicSerializer
from .source import SourceSerializer
from .variable import VizVariablePolymorphicSerializer
from ..models.viz import DataViz
from ..utils import DataResponse


class DataVizSerializer(serializers.HyperlinkedModelSerializer):
    variables = VizVariablePolymorphicSerializer(many=True)
    time_axis = TimeAxisPolymorphicSerializer()
    sources = SourceSerializer(many=True)

    class Meta:
        model = DataViz
        fields = (
            'id',
            'name',
            'slug',
            'viz_type',
            'description',
            'sources',
            'time_axis',
            'variables',
            'indicator',
        )


class DataVizWithDataSerializer(DataVizSerializer):
    data = serializers.SerializerMethodField()
    error = serializers.SerializerMethodField()
    geog = serializers.SerializerMethodField()

    class Meta:
        model = DataViz
        fields = DataVizSerializer.Meta.fields + ('data', 'error', 'geog', 'options')

    @lru_cache
    def _get_data_response(self, viz: DataViz, geog: CensusGeography) -> DataResponse:
        return viz.get_viz_data(geog)

    def get_data(self, obj: DataViz):
        if 'error' in self.context:
            return []
        data_response: DataResponse = self._get_data_response(obj, self.context['geography'])
        return data_response.data

    def get_error(self, obj: DataViz):
        if 'error' in self.context:
            return self.context['error']
        return self._get_data_response(obj, self.context['geography']).error.as_dict()

    def get_geog(self, obj: DataViz):
        return CensusGeographyPolymorphicSerializer(self.context['geography']).data


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
