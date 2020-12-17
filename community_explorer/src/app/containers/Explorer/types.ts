import { Region, RegionID, Taxonomy } from '../../types';

export interface ExplorerState {
  taxonomy?: Taxonomy;
  taxonomyIsLoading: boolean;
  taxonomyLoadError?: string;

  currentRegion?: Region;
  currentRegionIsLoading: boolean;
  currentRegionLoadError?: string;

  selectedGeoLayer: GeoLayer;
  selectedRegionID?: RegionID;
}

export type ContainerState = ExplorerState;

export interface GeoLayer {
  name: string;
  slug: MenuLayers;
  tableName: string;
  description: string;
}


export enum MenuLayers {
  BlockGroup = 'block-group',
  County = 'county',
  Tract = 'tract',
  CountySubdivision = 'county-subdivision',
}
