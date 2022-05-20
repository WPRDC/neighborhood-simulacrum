from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from context.serializers import TagSerializer, ContextItemSerializer
from indicators.models import TimeAxis, StaticTimeAxis, RelativeTimeAxis, StaticConsecutiveTimeAxis


class TimeAxisSerializer(serializers.HyperlinkedModelSerializer):
    class TimePartSerializer(serializers.Serializer):
        slug = serializers.CharField(max_length=255)
        name = serializers.CharField(max_length=255)
        time_point = serializers.DateTimeField()
        time_unit = serializers.CharField(max_length=20)

        def create(self, validated_data):
            return TimeAxis.TimePart(**validated_data)

        def update(self, instance: TimeAxis.TimePart, validated_data):
            instance.slug = validated_data.get('slug', instance.slug)
            instance.name = validated_data.get('name', instance.name)
            instance.time_point = validated_data.get('time_point', instance.time_point)
            instance.time_unit = validated_data.get('time_unit', instance.time_unit)

            return instance

    time_parts = TimePartSerializer(many=True)
    tags = TagSerializer(many=True)
    context = ContextItemSerializer(many=True)

    class Meta:
        model = TimeAxis
        fields = (
            'id',
            'name',
            'slug',
            'description',
            'unit',
            'time_parts',
        )


class StaticTimeAxisSerializer(TimeAxisSerializer):
    dates = serializers.ListField(child=serializers.DateTimeField())

    class Meta:
        model = StaticTimeAxis
        fields = TimeAxisSerializer.Meta.fields + (
            'dates',
        )


class StaticConsecutiveTimeAxisSerializer(TimeAxisSerializer):
    class Meta:
        model = StaticConsecutiveTimeAxis
        fields = TimeAxisSerializer.Meta.fields + (
            'start',
            'end',
            'ticks',
        )


class RelativeTimeAxisSerializer(TimeAxisSerializer):
    class Meta:
        model = RelativeTimeAxis
        fields = TimeAxisSerializer.Meta.fields + (
            'start_offset',
            'ticks',
            'direction',
        )


class TimeAxisPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        StaticTimeAxis: StaticTimeAxisSerializer,
        StaticConsecutiveTimeAxis: StaticConsecutiveTimeAxisSerializer,
        RelativeTimeAxis: RelativeTimeAxisSerializer,
    }
