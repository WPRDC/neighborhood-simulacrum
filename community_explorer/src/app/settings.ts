/*
 *
 * settings.ts
 *
 * App-level settings
 *
 */
import { MenuLayers } from './containers/Explorer/types';

export const MAPBOX_API_TOKEN =
  'pk.eyJ1Ijoic3RldmVuZHNheWxvciIsImEiOiJjazZxd2kyZGgwMTI3M250YWU5ZGhjemp1In0.YApLjyNK1QH77QnhRMdkKg';

// todo: maybe  replace with call to backend.
export const GEO_CATEGORIES: {
  name: string;
  slug: MenuLayers;
  tableName: string;
  description: string;
}[] = [
  {
    name: 'Counties',
    slug: MenuLayers.County,
    tableName: 'census_county',
    description: 'Largest subdivision of the state.',
  },
  {
    name: 'County Subdivisions',
    slug: MenuLayers.CountySubdivision,
    tableName: 'census_county_subdivision',
    description: 'Townships, municipalities, boroughs and cities.',
  },
  {
    name: 'Tracts',
    slug: MenuLayers.Tract,
    tableName: 'census_tract',
    description: 'Drawn to encompass ~2500-8000 people',
  },
  {
    name: 'Block Groups',
    slug: MenuLayers.BlockGroup,
    tableName: 'census_blockgroup',
    description: 'Smallest geographical unit w/ sample data.',
  },
];

export const DEFAULT_GEO_CATEGORY = GEO_CATEGORIES[2];
