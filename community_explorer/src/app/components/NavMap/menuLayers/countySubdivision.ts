import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayerItem } from '../types';
import { MenuLayer } from '../../../containers/Explorer/types';

const countySubdivision: MenuLayerItem = {
  slug: MenuLayer.CountySubdivision,
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
      id: `${MenuLayer.CountySubdivision}/hover`,
      type: 'fill',
      source: MenuLayer.CountySubdivision,
      'source-layer': MenuLayer.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayer.CountySubdivision}/selected`,
      type: 'fill',
      source: MenuLayer.CountySubdivision,
      'source-layer': MenuLayer.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'regionID', ''],
    },
    {
      id: `${MenuLayer.CountySubdivision}/borders`,
      type: 'line',
      source: MenuLayer.CountySubdivision,
      'source-layer': MenuLayer.CountySubdivision,
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
      id: `${MenuLayer.CountySubdivision}/fill`,
      type: 'fill',
      source: MenuLayer.CountySubdivision,
      'source-layer': MenuLayer.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default countySubdivision;
