import { LayerProps } from 'react-map-gl';
import { GeographyType } from '../../types';

export interface MenuLayerItem {
  slug: GeographyType;
  name: string;
  source: {
    type: 'vector' | 'raster';
    minzoom: number;
    maxzoom: number;
    source: string;
    sql: string;
  };
  layers: (LayerProps & { 'source-layer': string; id: string })[];
}
