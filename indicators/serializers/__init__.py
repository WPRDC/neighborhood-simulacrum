from rest_framework import serializers

from indicators.models import Domain, Subdomain, Indicator
from .time import TimeAxisPolymorphicSerializer, StaticTimeAxisSerializer, TimeAxisSerializer
from .source import (
    CensusSourceSerializer,
    CKANSourceSerializer,
    CKANRegionalSourceSerializer,
    CKANGeomSourceSerializer)
from .variable import CensusVariableSerializer, CKANVariableSerializer
from .viz import (
    DataVizIdentifiersPolymorphicSerializer,
    TableIdentifiersSerializer,
    DataVizPolymorphicSerializer,
    DataVizWithDataPolymorphicSerializer,
    TableSerializer,
    TableWithDataSerializer)


class IndicatorSerializer(serializers.HyperlinkedModelSerializer):
    data_vizes = DataVizIdentifiersPolymorphicSerializer(many=True)

    class Meta:
        model = Indicator
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'long_description',
            'limitations',
            'importance',
            'source',
            'provenance',
            'data_vizes',
        )


class SubdomainSerializer(serializers.ModelSerializer):
    indicators = IndicatorSerializer(many=True)

    class Meta:
        model = Subdomain
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'indicators',
        )


class DomainSerializer(serializers.ModelSerializer):
    subdomains = SubdomainSerializer(many=True)

    class Meta:
        model = Domain
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'subdomains',
        )
