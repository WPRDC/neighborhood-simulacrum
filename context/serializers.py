from rest_framework import serializers

from context.models import Tag, ContextItem


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'slug', 'name')


class ContextItemBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextItem
        fields = ('id', 'slug', 'name', 'level')


class ContextItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextItem
        fields = (
            'id',
            'slug',
            'name',
            'level',
            'text',
            'link',
        )
