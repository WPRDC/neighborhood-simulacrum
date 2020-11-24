from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from indicators.models import Series, YearSeries


@admin.register(Series)
class SeriesAdmin(PolymorphicParentModelAdmin):
    base_model = Series
    child_models = (YearSeries,)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class SeriesChildAdmin(PolymorphicChildModelAdmin):
    base_model = Series
    prepopulated_fields = {"slug": ("name",)}


@admin.register(YearSeries)
class YearSeriesAdmin(SeriesChildAdmin):
    pass
