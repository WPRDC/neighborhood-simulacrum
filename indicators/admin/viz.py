from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, StackedPolymorphicInline

from indicators.models import MiniMap, DataViz, Table, VizVariable

import nested_admin


class VizVariableInline(nested_admin.NestedTabularInline):
    model = VizVariable


@admin.register(DataViz)
class DataVizAdmin(PolymorphicParentModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
    base_model = DataViz
    child_models = (MiniMap, Table,)
    prepopulated_fields = {"slug": ("name",)}
    inlines = (VizVariableInline,)


class DataVizChildAdmin(PolymorphicChildModelAdmin):
    base_model = DataViz
    prepopulated_fields = {"slug": ("name",)}
    inlines = (VizVariableInline,)


@admin.register(MiniMap)
class MiniMapAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)


@admin.register(Table)
class TableAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)


class DataVizInline(nested_admin.NestedStackedPolymorphicInline):
    class MiniMapInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = MiniMap
        inlines = (VizVariableInline,)

    class TableInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = Table
        inlines = (VizVariableInline,)

    model = DataViz
    child_inlines = (
        MiniMapInline,
        TableInline,
    )
