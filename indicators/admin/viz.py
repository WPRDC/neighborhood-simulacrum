from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin, PolymorphicInlineSupportMixin

from indicators.models import MiniMap, DataViz, Table, OrderedVariable

import nested_admin

from indicators.models.viz import BarChart, LineChart, PieChart, PopulationPyramidChart, BigValue, Sentence, \
    GeogChoroplethMapLayer, ObjectsLayer, MapLayer, ParcelsLayer, TableRow, BarChartPart, \
    LineChartPart, PieChartPart, PopulationPyramidChartPart, SentenceVariable, BigValueVariable


@admin.register(DataViz)
class DataVizAdmin(PolymorphicParentModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
    base_model = DataViz
    child_models = (MiniMap, Table, BarChart, PieChart, LineChart, MiniMap)
    prepopulated_fields = {"slug": ("name",)}


class DataVizChildAdmin(nested_admin.NestedPolymorphicInlineSupportMixin, PolymorphicChildModelAdmin):
    """ Base class for all dataviz admins """
    base_model = DataViz
    prepopulated_fields = {"slug": ("name",)}


# inlines
class MapLayerInline(nested_admin.NestedStackedPolymorphicInline):
    class GeogChoroplethLayerInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = GeogChoroplethMapLayer
        autocomplete_fields = ('sub_geog', 'variable')

    class ObjectsLayerInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = ObjectsLayer
        autocomplete_fields = ('variable',)

    class ParcelsLayerInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = ParcelsLayer
        autocomplete_fields = ('variable',)

    model = MapLayer
    child_inlines = (
        GeogChoroplethLayerInline,
        ObjectsLayerInline,
        ParcelsLayerInline,
    )


class TableRowInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = TableRow


class BarChartPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = BarChartPart


class LineChartPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = LineChartPart


class PieChartPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = PieChartPart


class BigValueVariableInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = BigValueVariable


class SentenceVariableInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = SentenceVariable


class PopulationPyramidChartPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = PopulationPyramidChartPart


# ==================
# +  Map
# ==================
class MapLayerAdmin(PolymorphicParentModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name',)
    base_model = MapLayer
    child_models = (GeogChoroplethMapLayer, ObjectsLayer, ParcelsLayer,)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(MiniMap)
class MiniMapAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (MapLayerInline,)
    autocomplete_fields = ('time_axis',)


# ==================
# +  Table
# ==================
@admin.register(Table)
class TableAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (TableRowInline,)


# ==================
# +  Charts
# ==================
@admin.register(BarChart)
class BarChartAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (BarChartPartInline,)


@admin.register(LineChart)
class LineChartAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (LineChartPartInline,)


@admin.register(PieChart)
class PieChartAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (PieChartPartInline,)


@admin.register(PopulationPyramidChart)
class PopulationPyramidChartAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (PopulationPyramidChartPartInline,)


# ==================
# +  Alphanumeric
# ==================
@admin.register(BigValue)
class BigValueAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (BigValueVariableInline,)


@admin.register(Sentence)
class SentenceAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (SentenceVariableInline,)


class DataVizInline(nested_admin.NestedStackedPolymorphicInline):
    # Map
    class MiniMapInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = MiniMap
        inlines = (MapLayerInline,)

    # Table
    class TableInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = Table
        inlines = (TableRowInline,)

    # Chart
    class BarChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = BarChart
        inlines = (BarChartPartInline,)

    class LineChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = LineChart
        inlines = (LineChartPartInline,)

    class PieChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = PieChart
        inlines = (PieChartPartInline,)

    class PopulationPyramidChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = PopulationPyramidChart
        inlines = (PopulationPyramidChartPartInline,)

    # Alphanumeric
    class BigValueInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = BigValue
        inlines = (BigValueVariableInline,)

    class SentenceInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = Sentence
        inlines = (SentenceVariableInline,)

    model = DataViz
    child_inlines = (
        MiniMapInline,
        TableInline,
        BarChartInline,
        LineChartInline,
        PieChartInline,
        PopulationPyramidChartInline,
        BigValueInline,
        SentenceInline,
    )
