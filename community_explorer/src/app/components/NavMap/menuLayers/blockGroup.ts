import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayer } from '../types';
import { MenuLayers } from '../../../containers/Explorer/types';

export const blockGroup: MenuLayer = {
  slug: MenuLayers.BlockGroup,
  name: 'County Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_blockgroup',
    sql: `SELECT *, name as map_name, 'blockGroup' as regionType, geoid as regionID FROM census_blockgroup WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${MenuLayers.BlockGroup}/hover`,
      type: 'fill',
      source: MenuLayers.BlockGroup,
      'source-layer': MenuLayers.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'regionid', ''],
    },
    {
      id: `${MenuLayers.BlockGroup}/selected`,
      type: 'fill',
      source: MenuLayers.BlockGroup,
      'source-layer': MenuLayers.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'regionid', ''],
    },
    {
      id: `${MenuLayers.BlockGroup}/borders`,
      type: 'line',
      source: MenuLayers.BlockGroup,
      'source-layer': MenuLayers.BlockGroup,
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
      id: `${MenuLayers.BlockGroup}/fill`,
      type: 'fill',
      source: MenuLayers.BlockGroup,
      'source-layer': MenuLayers.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default blockGroup;
