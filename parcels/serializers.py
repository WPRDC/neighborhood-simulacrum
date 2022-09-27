from rest_framework import serializers

from .models import Parcel


class ParcelBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = (
            'parcel_id',
            'address',
        )


class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = (
            'parcel_id',
            'house_number',
            'street_name',
            'city',
            'state',
            'zip_code',
            'landmark_name',
            'post_box',
            'building_name',
        )
