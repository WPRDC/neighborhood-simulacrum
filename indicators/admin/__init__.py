from django.contrib import admin

from .series import SeriesAdmin, YearSeriesAdmin
from .source import CensusSourceAdmin, CKANSourceAdmin, CKANRegionalSourceAdmin, CKANGeomSourceAdmin
from .variable import VariableAdmin, CensusValueAdmin, CensusVariableAdmin, CKANVariableAdmin
from .viz import DataVizInline, DataVizAdmin, MiniMapAdmin, TableAdmin

from ..models import Indicator, Subdomain, Domain, Value

import nested_admin


class IndicatorInline(admin.StackedInline):
    model = Indicator


@admin.register(Indicator)
class IndicatorAdmin(nested_admin.NestedPolymorphicInlineSupportMixin, admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )
    inlines = (DataVizInline,)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subdomain)
class SubdomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    pass
