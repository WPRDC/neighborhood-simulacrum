from django.contrib import admin

from .source import CensusSourceAdmin, CKANSourceAdmin, CKANRegionalSourceAdmin, CKANGeomSourceAdmin
from .time import StaticTimeAxisAdmin, StaticConsecutiveTimeAxisAdmin, RelativeTimeAxisAdmin
from .variable import VariableAdmin, CensusVariableAdmin, CKANVariableAdmin
from .viz import DataVizInline, DataVizAdmin, MiniMapAdmin, TableAdmin
from ..models import Indicator, Subdomain, Domain, Value, SubdomainIndicator, IndicatorDataViz


class SubdomainIndicatorInline(admin.StackedInline):
    model = SubdomainIndicator


class IndicatorDataVizInline(admin.StackedInline):
    model = IndicatorDataViz
    autocomplete_fields = ('data_viz',)


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'description',
    )

    inlines = (IndicatorDataVizInline,)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Subdomain)
class SubdomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (SubdomainIndicatorInline,)


class SubdomainInline(admin.TabularInline):
    model = Subdomain


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

    inlines = (SubdomainInline,)


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    pass
