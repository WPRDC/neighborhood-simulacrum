import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayerItem } from '../types';
import { GeographyType } from '../../../types';

const tract: MenuLayerItem = {
  slug: GeographyType.Tract,
  name: 'County Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_tract',
    sql: `SELECT *, name as map_name, 'tract' as geogType, geoid as geogID FROM census_tract WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${GeographyType.Tract}/hover`,
      type: 'fill',
      source: GeographyType.Tract,
      'source-layer': GeographyType.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'geogID', ''],
    },
    {
      id: `${GeographyType.Tract}/selected`,
      type: 'fill',
      source: GeographyType.Tract,
      'source-layer': GeographyType.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'geogID', ''],
    },
    {
      id: `${GeographyType.Tract}/borders`,
      type: 'line',
      source: GeographyType.Tract,
      'source-layer': GeographyType.Tract,
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
      id: `${GeographyType.Tract}/fill`,
      type: 'fill',
      source: GeographyType.Tract,
      'source-layer': GeographyType.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default tract;
