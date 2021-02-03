from django.contrib import admin

from .time import StaticTimeAxisAdmin, StaticConsecutiveTimeAxisAdmin, RelativeTimeAxisAdmin
from .source import CensusSourceAdmin, CKANSourceAdmin, CKANRegionalSourceAdmin, CKANGeomSourceAdmin
from .variable import VariableAdmin, CensusVariableAdmin, CKANVariableAdmin
from .viz import DataVizInline, DataVizAdmin, MiniMapAdmin, TableAdmin

from ..models import Indicator, Subdomain, Domain, Value

import nested_admin  # todo: think about removing this as a dependence once we develop our own backend interface


class IndicatorInline(admin.StackedInline):
    model = Indicator


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


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    pass
