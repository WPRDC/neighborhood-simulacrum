import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayerItem } from '../types';
import { GeographyType } from '../../../types';

const census: MenuLayerItem = {
  slug: GeographyType.County,
  name: 'County Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_county',
    sql: `SELECT *, name as map_name, 'county' as geogType, geoid as geogID FROM census_county WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${GeographyType.County}/hover`,
      type: 'fill',
      source: GeographyType.County,
      'source-layer': GeographyType.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'geogID', ''],
    },
    {
      id: `${GeographyType.County}/selected`,
      type: 'fill',
      source: GeographyType.County,
      'source-layer': GeographyType.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'geogID', ''],
    },
    {
      id: `${GeographyType.County}/borders`,
      type: 'line',
      source: GeographyType.County,
      'source-layer': GeographyType.County,
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
      id: `${GeographyType.County}/fill`,
      type: 'fill',
      source: GeographyType.County,
      'source-layer': GeographyType.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default census;
