from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from indicators.models import Variable, CensusVariable, CKANVariable
from indicators.models.variable import CensusValue, CensusVariableSource


@admin.register(Variable)
class VariableAdmin(PolymorphicParentModelAdmin):
    base_model = Variable
    child_models = (CKANVariable, CensusVariable,)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}
    list_display = (
        'slug',
        'name',
        'title',
        'id'
    )


class VariableChildAdmin(PolymorphicChildModelAdmin):
    base_model = Variable
    prepopulated_fields = {"slug": ("name",)}


class CensusVariableSourceInline(admin.TabularInline):
    model = CensusVariableSource


@admin.register(CensusVariable)
class CensusVariableAdmin(VariableChildAdmin):
    list_display = (
        'id',
        'name',
        'title',
    )
    list_filter = ('sources',)
    search_fields = ('name',)
    inlines = (CensusVariableSourceInline,)


@admin.register(CensusValue)
class CensusValueAdmin(admin.ModelAdmin):
    list_display = ('census_table', 'geography', 'value')
    search_fields = ('census_table',)
    autocomplete_fields = ('geography',)


@admin.register(CKANVariable)
class CKANVariableAdmin(VariableChildAdmin):
    list_display = (
        'id',
        'name',
        'title',
    )
    list_filter = ('sources',)
    search_fields = ('name',)
