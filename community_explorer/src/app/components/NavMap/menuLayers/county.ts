import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayer } from '../types';
import { MenuLayers } from '../../../containers/Explorer/types';

const census: MenuLayer = {
  slug: MenuLayers.County,
  name: 'County Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_county',
    sql: `SELECT *, 'county' as regionType FROM census_county WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${MenuLayers.County}/hover`,
      type: 'fill',
      source: MenuLayers.County,
      'source-layer': MenuLayers.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'geoid', ''],
    },
    {
      id: `${MenuLayers.County}/selected`,
      type: 'fill',
      source: MenuLayers.County,
      'source-layer': MenuLayers.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'geoid', ''],
    },
    {
      id: `${MenuLayers.County}/borders`,
      type: 'line',
      source: MenuLayers.County,
      'source-layer': MenuLayers.County,
      layout: {
        'line-join': 'round',
      },
      paint: {
        'line-width': theme.polygons.lineWidth.dense,
        'line-opacity': theme.polygons.lineOpacity.standard,
        'line-color': theme.polygons.lineColor,
      },
    },
    {
      id: `${MenuLayers.County}/fill`,
      type: 'fill',
      source: MenuLayers.County,
      'source-layer': MenuLayers.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default census;
