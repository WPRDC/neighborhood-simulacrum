import county from './county';
import countySubdivision from './countySubdivision';
import tract from './tract';
import blockGroup from './blockGroup';
import { MenuLayer } from '../types';
import { MenuLayers } from '../../../containers/Explorer/types';

const menuLayers: Record<MenuLayers, MenuLayer> = {
  [MenuLayers.County]: county,
  [MenuLayers.CountySubdivision]: countySubdivision,
  [MenuLayers.BlockGroup]: blockGroup,
  [MenuLayers.Tract]: tract,
};
export default menuLayers;
