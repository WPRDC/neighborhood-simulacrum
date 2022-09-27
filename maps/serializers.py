from rest_framework import serializers

from context.serializers import TagSerializer, ContextItemSerializer
from maps.models import IndicatorLayer, CKANLayer, MapLayer


class DataLayerSerializer(serializers.ModelSerializer):
    """ Basic information for DataLayer"""

    class Meta:
        model = IndicatorLayer
        fields = (
            'id',
            'name',
            'slug',
            'description',
        )


class IndicatorLayerDetailsSerializer(serializers.ModelSerializer):
    """ Includes the fields that require computation """
    sources = serializers.JSONField()
    layers = serializers.JSONField()

    class Meta:
        model = IndicatorLayer
        fields = (
            'id',
            'name',
            'slug',
            'description',
            # mapbox stuff
            'sources',
            'layers',
            'interactive_layer_ids',
            # our stuff
            'legend'
        )


class MapLayerBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapLayer
        fields = (
            'slug',
            'name',
            'geog_type',
            'description',
        )


class MapLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapLayer
        fields = (
            'slug',
            'name',
            'description',
            'geog_type',
            'source',
            'layers',
            'legend',
        )


class CKANLayerSerializer(MapLayerSerializer):
    class Meta:
        model = CKANLayer
        fields = MapLayerSerializer.Meta.fields + (
            'resource',
            'package',
        )
