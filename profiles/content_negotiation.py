import json

from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.renderers import BaseRenderer
from rest_framework.request import Request


class GeoJSONRenderer(BaseRenderer):
    media_type = 'application/geo+json'
    format = 'geojson'

    def render(self, data, media_type=None, renderer_context=None):
        return json.dumps(data)


class GeoJSONContentNegotiation(BaseContentNegotiation):
    """ Custom content negotiation scheme for GeoJSON files. """

    def select_parser(self, request, parsers):
        return super(GeoJSONContentNegotiation, self).select_parser(request, parsers)

    def select_renderer(self, request: Request, renderers, format_suffix=None):
        renderer = renderers[0]
        if request.query_params.get('download', False):
            renderer = GeoJSONRenderer()
        return renderer, renderer.media_type
