from rest_framework import serializers

from context.serializers import TagSerializer, ContextItemSerializer
from indicators.models import CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource, Source


class SourceSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)

    class Meta:
        model = Source
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'info_link',
            'tags',
            'context',
        )


# Census
class CensusSourceSerializer(SourceSerializer):
    class Meta:
        model = CensusSource
        fields = SourceSerializer.Meta.fields + ('dataset',)


# CKAN
class CKANSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CKANSource
        fields = SourceSerializer.Meta.fields + ('package_id', 'resource_id',)


class CKANGeomSourceSerializer(CKANSourceSerializer):
    class Meta:
        model = CKANGeomSource
        fields = CKANSourceSerializer.Meta.fields


class CKANRegionalSourceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CKANRegionalSource
        fields = CKANSourceSerializer.Meta.fields
