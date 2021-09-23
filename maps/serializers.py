from rest_framework import serializers

from maps.models import DataLayer


class DataLayerSerializer(serializers.ModelSerializer):
    """ Basic information for DataLayer"""
    class Meta:
        model = DataLayer
        fields = (
            'id',
            'name',
            'slug',
            'description',
        )


class DataLayerDetailsSerializer(serializers.ModelSerializer):
    """ Includes the fields that require computation """
    class Meta:
        model = DataLayer
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
