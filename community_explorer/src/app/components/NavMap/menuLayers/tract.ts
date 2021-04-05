import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayerItem } from '../types';
import { MenuLayer } from '../../../containers/Explorer/types';

const tract: MenuLayerItem = {
  slug: MenuLayer.Tract,
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
      id: `${MenuLayer.Tract}/hover`,
      type: 'fill',
      source: MenuLayer.Tract,
      'source-layer': MenuLayer.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayer.Tract}/selected`,
      type: 'fill',
      source: MenuLayer.Tract,
      'source-layer': MenuLayer.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayer.Tract}/borders`,
      type: 'line',
      source: MenuLayer.Tract,
      'source-layer': MenuLayer.Tract,
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
      id: `${MenuLayer.Tract}/fill`,
      type: 'fill',
      source: MenuLayer.Tract,
      'source-layer': MenuLayer.Tract,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default tract;
