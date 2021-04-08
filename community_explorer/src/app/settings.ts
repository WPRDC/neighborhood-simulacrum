/*
 *
 * settings.ts
 *
 * App-level settings
 *
 */
import { GeogTypeDescriptor } from './containers/Explorer/types';

import { GeogDescriptor, GeographyType } from './types';

export const MAPBOX_API_TOKEN =
  'pk.eyJ1Ijoic3RldmVuZHNheWxvciIsImEiOiJja2xtdTluczcwY3U0Mm5rMGw2ZXFkNjJxIn0.dw1OGgmTsSUP1A-zCsAGQw';

// todo: maybe  replace with call to backend.

export const GEOG_TYPES: GeogTypeDescriptor[] = [
  {
    name: 'Counties',
    id: GeographyType.County,
    tableName: 'census_county',
    description: 'Largest subdivision of the state.',
  },
  {
    name: 'County Subdivisions',
    id: GeographyType.CountySubdivision,
    tableName: 'census_county_subdivision',
    description: 'Townships, municipalities, boroughs and cities.',
  },
  {
    name: 'Tracts',
    id: GeographyType.Tract,
    tableName: 'census_tract',
    description: 'Drawn to encompass ~2500-8000 people',
  },
  {
    name: 'Block Groups',
    id: GeographyType.BlockGroup,
    tableName: 'census_blockgroup',
    description: 'Smallest geographical unit w/ sample data.',
  },
];

export const DEFAULT_GEOG_TYPE = GEOG_TYPES[1];

export const DEFAULT_GEOG: GeogDescriptor = {
  id: 16592,
  title: 'Pittsburgh',
  geogType: GeographyType.CountySubdivision,
  geogID: '4200361000',
};
