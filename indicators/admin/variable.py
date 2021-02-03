from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from indicators.models import Variable, CensusVariable, CKANVariable
from indicators.models.variable import CensusVariableSource


@admin.register(Variable)
class VariableAdmin(PolymorphicParentModelAdmin):
    base_model = Variable
    child_models = (CKANVariable, CensusVariable,)
    search_fields = ('name', 'slug')
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
    autocomplete_fields = ('denominators',)


class CensusVariableSourceInline(admin.TabularInline):
    model = CensusVariableSource
    autocomplete_fields = ('census_table_pointers',)


@admin.register(CensusVariable)
class CensusVariableAdmin(VariableChildAdmin):
    list_display = (
        'id',
        'name',
        'title',
    )
    list_filter = ('sources',)
    search_fields = ('name', 'slug')
    inlines = (CensusVariableSourceInline,)
    autocomplete_fields = ('denominators',)


@admin.register(CKANVariable)
class CKANVariableAdmin(VariableChildAdmin):
    list_display = (
        'id',
        'name',
        'title',
    )
    list_filter = ('sources',)
    search_fields = ('name', 'slug',)
    autocomplete_fields = ('denominators',)
