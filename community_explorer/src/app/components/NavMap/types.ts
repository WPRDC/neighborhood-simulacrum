import { LayerProps } from 'react-map-gl';
import { MenuLayer } from '../../containers/Explorer/types';

export interface MenuLayerItem {
  slug: MenuLayer;
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
