from django.contrib import admin

from .time import StaticTimeAxisAdmin, StaticConsecutiveTimeAxisAdmin, RelativeTimeAxisAdmin
from .source import CensusSourceAdmin, CKANSourceAdmin, CKANRegionalSourceAdmin, CKANGeomSourceAdmin
from .variable import VariableAdmin, CensusVariableAdmin, CKANVariableAdmin
from .viz import DataVizInline, DataVizAdmin, MiniMapAdmin, TableAdmin

from ..models import Indicator, Subdomain, Domain, Value, SubdomainIndicator

import nested_admin  # todo: think about removing this as a dependency once we develop our own backend interface


class SubdomainIndicatorInline(admin.StackedInline):
    model = SubdomainIndicator


@admin.register(Indicator)
class IndicatorAdmin(nested_admin.NestedPolymorphicModelAdmin):
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
