from django.contrib import admin
from django.contrib.admin import register, ModelAdmin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from maps.models import CKANLayer, MapLayer, IndicatorLayer


@register(MapLayer)
class MapLayerAdmin(PolymorphicParentModelAdmin):
    base_model = MapLayer
    child_models = (CKANLayer,)
    search_fields = ('name', 'slug',)
    prepopulated_fields = {"slug": ("name",)}
    list_display = (
        'slug',
        'name',
    )


class MapLayerChildAdmin(PolymorphicChildModelAdmin):
    base_model = MapLayer
    prepopulated_fields = {"slug": ("name",)}


@register(CKANLayer)
class CKANLayerAdmin(MapLayerChildAdmin):
    list_display = ('slug', 'name',)
    search_fields = ('name', 'slug',)


@register(IndicatorLayer)
class IndicatorLayerAdmin(ModelAdmin):
    pass
