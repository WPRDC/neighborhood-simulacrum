from django.contrib import admin

from indicators.models import Indicator, IndicatorVariable


class IndicatorVariableInline(admin.TabularInline):
    model = IndicatorVariable


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name',)
    search_fields = ('name', 'slug', 'description',)
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ('time_axis', 'vars',)
    inlines = (IndicatorVariableInline,)
