from typing import Optional, Type, TYPE_CHECKING

from django.db import models
from django.db.models import QuerySet, Manager
from django.utils.text import slugify
from polymorphic.models import PolymorphicModel

from indicators.data import Datum, GeogCollection
from indicators.utils import ErrorRecord
from maps.models import DataLayer
from maps.util import menu_view_name

if TYPE_CHECKING:
    from .. import Variable
    from geo.models import AdminRegion

from .common import DataViz, VizVariable


class MiniMap(DataViz):
    BORDER_LAYER_BASE = {
        "type": "line",
        "paint": {
            "line-color": "#000",
            "line-width": [
                "interpolate",
                ["exponential", 1.51],
                ["zoom"],
                0, 1,
                8, 4,
                16, 14
            ]
        },
    }
    vars: Manager['Variable'] = models.ManyToManyField('Variable', verbose_name='Layers', through='MapLayer')

    @property
    def layers(self):
        return self.vars.all()

    def get_neighbor_geogs(self, geog: 'AdminRegion') -> QuerySet['AdminRegion']:
        geog_type = geog.__class__
        # get all geogs of type for now
        # todo: provide options to allow for different neighbor selection
        return geog_type.objects.filter(in_extent=True)

    def _get_viz_data(
            self,
            geogs: QuerySet['AdminRegion'],
            parent_geog_lvl: Optional[Type['AdminRegion']] = None
    ) -> (list[Datum], list[ErrorRecord]):
        return [], []  # map data is stored in geojson that is served elsewhere

    def _get_viz_options(self, geog_collection: GeogCollection) -> dict:
        """
        Collects and returns the data for this presentation at the `geog` provided

        Cross-geography presentations will cached. keyed in part by `type(geog)`
        as the data returned is the same for any target geog of the same type
        """
        sources: [dict] = []
        layers: [dict] = []
        interactive_layer_ids: [str] = []
        legend_options: [dict] = []

        for var in self.vars.all():
            # for each variable/layer, get its data geojson, style and options
            # MapLayer object keeps track of settings from editor
            layer: MapLayer = self.vars.through.objects.get(variable=var, viz=self)
            data_layer: DataLayer = layer.get_data_layer(geog_collection)
            source, tmp_layers, interactive_layer_ids, legend_option = data_layer.get_map_options()
            sources.append(source)
            legend_options.append(legend_option)
            layers += tmp_layers

        primary_geog = geog_collection.primary_geog

        map_options: dict = {
            'interactive_layer_ids': interactive_layer_ids,
            'default_viewport': {
                'longitude': primary_geog.geom.centroid.x,
                'latitude': primary_geog.geom.centroid.y,
                'zoom': primary_geog.base_zoom - 1
            }
        }

        # for highlighting current geog
        highlight_id = slugify(primary_geog.name)
        highlight_source = {
            'id': f'{highlight_id}',
            'type': 'vector',
            'url': f"https://api.profiles.wprdc.org/tiles/{menu_view_name(geog_collection.geog_type)}.json",
        }
        highlight_layer = {
            'id': f'{highlight_id}/highlight',
            'source': f'{highlight_id}',
            'source-layer': f'{highlight_id}',
            **self.BORDER_LAYER_BASE
        }
        sources.append(highlight_source)
        layers.append(highlight_layer)

        return {'sources': sources,
                'layers': layers,
                'legends': legend_options,
                'map_options': map_options}


class MapLayer(PolymorphicModel, VizVariable):
    """ Base class for map layers """
    viz = models.ForeignKey('MiniMap', on_delete=models.CASCADE, related_name='mini_map_to_variable')
    variable = models.ForeignKey('Variable', on_delete=models.CASCADE, related_name='variable_to_mini_map')

    # options
    visible = models.BooleanField(verbose_name='Visible by default', default=True)
    use_percent = models.BooleanField(default=False)

    # mapbox style
    custom_paint = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                    blank=True, null=True)
    custom_layout = models.JSONField(help_text='https://docs.mapbox.com/help/glossary/layout-paint-property/',
                                     blank=True, null=True)

    def get_data_layer(self, geog_collection: 'GeogCollection'):
        return DataLayer.get_or_create_updated_map(geog_collection, self.viz.time_axis, self.variable, self.use_percent)
