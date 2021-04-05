import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayerItem } from '../types';
import { MenuLayer } from '../../../containers/Explorer/types';

const census: MenuLayerItem = {
  slug: MenuLayer.County,
  name: 'County Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_county',
    sql: `SELECT *, name as map_name, 'county' as regionType, geoid as regionID FROM census_county WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${MenuLayer.County}/hover`,
      type: 'fill',
      source: MenuLayer.County,
      'source-layer': MenuLayer.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayer.County}/selected`,
      type: 'fill',
      source: MenuLayer.County,
      'source-layer': MenuLayer.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayer.County}/borders`,
      type: 'line',
      source: MenuLayer.County,
      'source-layer': MenuLayer.County,
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
      id: `${MenuLayer.County}/fill`,
      type: 'fill',
      source: MenuLayer.County,
      'source-layer': MenuLayer.County,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default census;
