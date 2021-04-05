import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayerItem } from '../types';
import { MenuLayer } from '../../../containers/Explorer/types';

export const blockGroup: MenuLayerItem = {
  slug: MenuLayer.BlockGroup,
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
      id: `${MenuLayer.BlockGroup}/hover`,
      type: 'fill',
      source: MenuLayer.BlockGroup,
      'source-layer': MenuLayer.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'regionid', ''],
    },
    {
      id: `${MenuLayer.BlockGroup}/selected`,
      type: 'fill',
      source: MenuLayer.BlockGroup,
      'source-layer': MenuLayer.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'regionid', ''],
    },
    {
      id: `${MenuLayer.BlockGroup}/borders`,
      type: 'line',
      source: MenuLayer.BlockGroup,
      'source-layer': MenuLayer.BlockGroup,
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
      id: `${MenuLayer.BlockGroup}/fill`,
      type: 'fill',
      source: MenuLayer.BlockGroup,
      'source-layer': MenuLayer.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default blockGroup;
