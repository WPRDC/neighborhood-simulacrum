import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayer } from '../types';
import { MenuLayers } from '../../../containers/Explorer/types';

const tract: MenuLayer = {
  slug: MenuLayers.Tract,
  name: 'County Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_tract',
    sql: `SELECT *, name as map_name, 'tract' as regionType, geoid as regionID FROM census_tract WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${MenuLayers.Tract}/hover`,
      type: 'fill',
      source: MenuLayers.Tract,
      'source-layer': MenuLayers.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayers.Tract}/selected`,
      type: 'fill',
      source: MenuLayers.Tract,
      'source-layer': MenuLayers.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayers.Tract}/borders`,
      type: 'line',
      source: MenuLayers.Tract,
      'source-layer': MenuLayers.Tract,
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
      id: `${MenuLayers.Tract}/fill`,
      type: 'fill',
      source: MenuLayers.Tract,
      'source-layer': MenuLayers.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default tract;
