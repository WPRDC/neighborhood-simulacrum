import nested_admin
from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from indicators.models.viz import (
    DataViz,
    MiniMap,
    Table,
    BigValue,
    Sentence,
    TableVariable,
    MapLayer,
    SentenceVariable,
    BigValueVariable,
    BarChart,
    LineChart,
    PieChart,
    PyramidChart,
    ScatterPlot,
    Histogram
)


@admin.register(DataViz)
class DataVizAdmin(PolymorphicParentModelAdmin, nested_admin.NestedPolymorphicInlineSupportMixin):
    list_display = ('slug', 'name',)
    search_fields = ('name', 'slug')
    base_model = DataViz
    child_models = (
        MiniMap,
        Table,
        MiniMap,
        BigValue,
        Sentence,
        BarChart,
        LineChart,
        PieChart,
        PyramidChart,
        ScatterPlot,
        Histogram
    )
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ('time_axis',)


class DataVizChildAdmin(nested_admin.NestedPolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    """ Base class for all dataviz admins """
    base_model = DataViz
    prepopulated_fields = {"slug": ("name",)}


# inlines
class MapLayerInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = MapLayer


class TableRowInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = TableVariable


class BigValueVariableInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = BigValueVariable


class SentenceVariableInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = SentenceVariable


class BarChartPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = BarChart.BarChartPart


class LineChartPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = LineChart.LineChartPart


class PieChartPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = PieChart.PieChartPart


class PyramidChartLeftPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = PyramidChart.PyramidChartLeftPart


class PyramidChartRightPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = PyramidChart.PyramidChartRightPart


@admin.register(MiniMap)
class MiniMapAdmin(DataVizChildAdmin):
    inlines = (MapLayerInline,)


@admin.register(Table)
class TableAdmin(DataVizChildAdmin):
    inlines = (TableRowInline,)


@admin.register(BigValue)
class BigValueAdmin(DataVizChildAdmin):
    inlines = (BigValueVariableInline,)


@admin.register(Sentence)
class SentenceAdmin(DataVizChildAdmin):
    inlines = (SentenceVariableInline,)


@admin.register(BarChart)
class BarChartAdmin(DataVizChildAdmin):
    inlines = (BarChartPartInline,)


@admin.register(LineChart)
class LineChartAdmin(DataVizChildAdmin):
    inlines = (LineChartPartInline,)


@admin.register(PieChart)
class PieChartAdmin(DataVizChildAdmin):
    inlines = (PieChartPartInline,)


@admin.register(PyramidChart)
class PyramidChartAdmin(DataVizChildAdmin):
    inlines = (PyramidChartLeftPartInline, PyramidChartRightPartInline,)


@admin.register(ScatterPlot)
class ScatterPlotAdmin(DataVizChildAdmin):
    pass


@admin.register(Histogram)
class HistogramAdmin(DataVizChildAdmin):
    pass


class DataVizInline(nested_admin.NestedStackedPolymorphicInline):
    # Map
    class MiniMapInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = MiniMap
        inlines = (MapLayerInline,)

    # Table
    class TableInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = Table
        inlines = (TableRowInline,)

    # Alphanumeric
    class BigValueInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = BigValue
        inlines = (BigValueVariableInline,)

    class SentenceInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = Sentence
        inlines = (SentenceVariableInline,)

    # Charts
    class BarChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = BarChart
        inlines = (BarChartPartInline,)

    class LineChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = LineChart
        inlines = (LineChartPartInline,)

    class PieChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = PieChart
        inlines = (PieChartPartInline,)

    class PyramidChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = PyramidChart
        inlines = (PyramidChartLeftPartInline, PyramidChartRightPartInline,)

    class ScatterPlotInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = ScatterPlot

    class HistogramInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = Histogram

    model = DataViz
    child_inlines = (
        MiniMapInline,
        TableInline,
        BigValueInline,
        SentenceInline,
        BarChartInline,
        LineChartInline,
        PieChartInline,
        PyramidChartInline,
        ScatterPlotInline,
        HistogramInline
    )
