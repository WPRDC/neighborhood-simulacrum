from rest_framework import serializers

from indicators.models import CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource


class CensusSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CensusSource
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'dataset',
        )


class CKANSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CKANSource
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'package_id',
            'resource_id',
        )


class CKANGeomSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CKANGeomSource
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'package_id',
            'resource_id',
        )


class CKANRegionalSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CKANRegionalSource
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'package_id',
            'resource_id',
        )
