from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from indicators.models import CensusSource, CKANSource, CKANGeomSource, CKANRegionalSource


@admin.register(CensusSource)
class CensusSourceAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
        'dataset',
    )
    autocomplete_fields = ('geographic_extent',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CKANSource)
class CKANSourceAdmin(PolymorphicParentModelAdmin):
    list_display = (
        'name',
        'slug',
        'package_id',
        'resource_id'
    )
    search_fields = ('name',)
    base_model = CKANSource
    autocomplete_fields = ('geographic_extent',)
    child_models = (CKANGeomSource, CKANRegionalSource,)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CKANGeomSource)
class CKANGeomSourceAdmin(PolymorphicChildModelAdmin):
    base_model = CKANGeomSource
    list_display = (
        'name',
        'slug',
        'package_id',
        'resource_id',
        'geom_field',
    )
    search_fields = ('name',)
    autocomplete_fields = ('geographic_extent',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CKANRegionalSource)
class CKANRegionalSourceAdmin(PolymorphicChildModelAdmin):
    base_model = CKANRegionalSource
    list_display = (
        'name',
        'slug',
        'package_id',
        'resource_id',
    )
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ('geographic_extent',)
