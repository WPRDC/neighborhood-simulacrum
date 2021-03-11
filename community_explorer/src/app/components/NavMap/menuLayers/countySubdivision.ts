import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayer } from '../types';
import { MenuLayers } from '../../../containers/Explorer/types';

const countySubdivision: MenuLayer = {
  slug: MenuLayers.CountySubdivision,
  name: 'County Subdivision Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_county_subdivision',
    sql: `SELECT * , name as map_name, 'countySubdivision' as regionType, geoid as regionID FROM census_county_subdivision WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${MenuLayers.CountySubdivision}/hover`,
      type: 'fill',
      source: MenuLayers.CountySubdivision,
      'source-layer': MenuLayers.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayers.CountySubdivision}/selected`,
      type: 'fill',
      source: MenuLayers.CountySubdivision,
      'source-layer': MenuLayers.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayers.CountySubdivision}/borders`,
      type: 'line',
      source: MenuLayers.CountySubdivision,
      'source-layer': MenuLayers.CountySubdivision,
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
      id: `${MenuLayers.CountySubdivision}/fill`,
      type: 'fill',
      source: MenuLayers.CountySubdivision,
      'source-layer': MenuLayers.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default countySubdivision;
