import nested_admin
from django.contrib import admin
from polymorphic.admin import PolymorphicParentModelAdmin, PolymorphicChildModelAdmin

from indicators.models.viz import DataViz, MiniMap, Table, Chart, \
    BigValue, Sentence, GeogChoroplethMapLayer, \
    ObjectsLayer, TableRow, ChartPart, MapLayer, ParcelsLayer, SentenceVariable, BigValueVariable


@admin.register(DataViz)
class DataVizAdmin(PolymorphicParentModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('name',)
    base_model = DataViz
    child_models = (MiniMap, Table, Chart, MiniMap, BigValue, Sentence)
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


class TableRowInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = TableRow


class ChartPartInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = ChartPart


class BigValueVariableInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = BigValueVariable


class SentenceVariableInline(nested_admin.NestedTabularInline):
    autocomplete_fields = ('variable',)
    model = SentenceVariable


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


@admin.register(Table)
class TableAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (TableRowInline,)


@admin.register(Chart)
class ChartAdmin(DataVizChildAdmin):
    list_display = (
        'name',
    )
    search_fields = ('name',)
    inlines = (ChartPartInline,)


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
    class ChartInline(nested_admin.NestedStackedPolymorphicInline.Child):
        model = Chart
        inlines = (ChartPartInline,)


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
        ChartInline,
        BigValueInline,
        SentenceInline,
    )
