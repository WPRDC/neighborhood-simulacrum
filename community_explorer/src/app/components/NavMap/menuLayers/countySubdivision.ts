import { censusFilter } from '../settings';
import theme from '../theme';
import { MenuLayerItem } from '../types';
import { GeographyType } from '../../../types';

const countySubdivision: MenuLayerItem = {
  slug: GeographyType.CountySubdivision,
  name: 'County Subdivision Boundaries',
  source: {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: 'census_county_subdivision',
    sql: `SELECT * , name as map_name, 'countySubdivision' as geogType, geoid as geogID FROM census_county_subdivision WHERE statefp = '42' AND ${censusFilter}`,
  },
  layers: [
    {
      id: `${GeographyType.CountySubdivision}/hover`,
      type: 'fill',
      source: GeographyType.CountySubdivision,
      'source-layer': GeographyType.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'geogID', ''],
    },
    {
      id: `${GeographyType.CountySubdivision}/selected`,
      type: 'fill',
      source: GeographyType.CountySubdivision,
      'source-layer': GeographyType.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'geogID', ''],
    },
    {
      id: `${GeographyType.CountySubdivision}/borders`,
      type: 'line',
      source: GeographyType.CountySubdivision,
      'source-layer': GeographyType.CountySubdivision,
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
      id: `${GeographyType.CountySubdivision}/fill`,
      type: 'fill',
      source: GeographyType.CountySubdivision,
      'source-layer': GeographyType.CountySubdivision,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ],
};

export default countySubdivision;
