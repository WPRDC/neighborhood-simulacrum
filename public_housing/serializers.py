from rest_framework import serializers
from public_housing.models import ProjectIndex


class CensusGeographyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectIndex
        fields = (
            'id',
            'property_id',
            'hud_property_name',
            'municipality_name',
            'city',
            'zip_code',
            'units',
            'scattered_sites',
            'latitude',
            'longitude',
            'census_tract',
            'crowdsourced_id',
            'house_cat_id',
            'status',
        )
