from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, StackedPolymorphicInline

from indicators.models import MiniMap, DataViz, Table, VizVariable

import nested_admin

from indicators.models.viz import BarChart, LineChart, PieChart, PopulationPyramidChart, BigValue, Sentence


class VizVariableInline(nested_admin.NestedTabularInline):
    model = VizVariable
    autocomplete_fields = ('variable',)


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


@admin.register(BigValue)
class BigValueAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)


@admin.register(Sentence)
class SentenceAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)


@admin.register(BarChart)
class BarChartAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)


@admin.register(LineChart)
class LineChartAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)


@admin.register(PieChart)
class PieChartAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)


@admin.register(PopulationPyramidChart)
class PopulationPyramidChartAdmin(DataVizChildAdmin):
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

    class BarChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = BarChart
        inlines = (VizVariableInline,)

    class BigValueInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = BigValue
        inlines = (VizVariableInline,)

    class SentenceInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = Sentence
        inlines = (VizVariableInline,)

    class LineChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = LineChart
        inlines = (VizVariableInline,)

    class PieChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = PieChart
        inlines = (VizVariableInline,)

    class PopulationPyramidChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = PopulationPyramidChart
        inlines = (VizVariableInline,)

    model = DataViz
    child_inlines = (
        MiniMapInline,
        TableInline,
        BigValueInline,
        SentenceInline,
        BarChartInline,
        LineChartInline,
        PieChartInline,
        PopulationPyramidChartInline,
    )
