from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from indicators.models import TimeAxis, StaticTimeAxis, StaticConsecutiveTimeAxis, RelativeTimeAxis


@admin.register(TimeAxis)
class TimeFrameAdmin(PolymorphicParentModelAdmin):
    base_model = TimeAxis
    child_models = (StaticTimeAxis, StaticConsecutiveTimeAxis, RelativeTimeAxis,)
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}


class TimeAxisChildAdmin(PolymorphicChildModelAdmin):
    base_model = TimeAxis
    prepopulated_fields = {"slug": ("name",)}


@admin.register(StaticTimeAxis)
class StaticTimeAxisAdmin(TimeAxisChildAdmin):
    pass


@admin.register(StaticConsecutiveTimeAxis)
class StaticConsecutiveTimeAxisAdmin(TimeAxisChildAdmin):
    pass


@admin.register(RelativeTimeAxis)
class RelativeTimeAxisAdmin(TimeAxisChildAdmin):
    pass
