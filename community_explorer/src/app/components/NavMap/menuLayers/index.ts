import county from './county';
import countySubdivision from './countySubdivision';
import tract from './tract';
import blockGroup from './blockGroup';
import { MenuLayer } from '../../../containers/Explorer/types';
import {MenuLayerItem} from "../types";

const menuLayers: Record<MenuLayer, MenuLayerItem> = {
  [MenuLayer.County]: county,
  [MenuLayer.CountySubdivision]: countySubdivision,
  [MenuLayer.BlockGroup]: blockGroup,
  [MenuLayer.Tract]: tract,
};
export default menuLayers;
