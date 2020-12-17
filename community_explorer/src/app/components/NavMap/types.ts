import { LayerProps } from 'react-map-gl';
import { MenuLayers } from '../../containers/Explorer/types';

export interface MenuLayer {
  slug: MenuLayers;
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
