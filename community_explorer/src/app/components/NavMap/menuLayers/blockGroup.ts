import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayerItem } from '../types';
import { GeographyType } from '../../../types';

export const blockGroup: MenuLayerItem = {
  slug: GeographyType.BlockGroup,
  name: 'County Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_blockgroup',
    sql: `SELECT *, name as map_name, 'blockGroup' as geogType, geoid as geogID FROM census_blockgroup WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${GeographyType.BlockGroup}/hover`,
      type: 'fill',
      source: GeographyType.BlockGroup,
      'source-layer': GeographyType.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'geogid', ''],
    },
    {
      id: `${GeographyType.BlockGroup}/selected`,
      type: 'fill',
      source: GeographyType.BlockGroup,
      'source-layer': GeographyType.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'geogid', ''],
    },
    {
      id: `${GeographyType.BlockGroup}/borders`,
      type: 'line',
      source: GeographyType.BlockGroup,
      'source-layer': GeographyType.BlockGroup,
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
      id: `${GeographyType.BlockGroup}/fill`,
      type: 'fill',
      source: GeographyType.BlockGroup,
      'source-layer': GeographyType.BlockGroup,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default blockGroup;
