import { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from 'utils/@reduxjs/toolkit';
import { ContainerState, GeoLayer } from './types';
import { DEFAULT_GEO_CATEGORY } from '../../settings';
import { Region, RegionDescriptor, Taxonomy } from '../../types';

// The initial state of the Explorer container
export const initialState: ContainerState = {
  taxonomy: undefined,
  taxonomyIsLoading: false,
  taxonomyLoadError: undefined,

  currentRegion: undefined,
  currentRegionIsLoading: false,
  currentRegionLoadError: undefined,

  // menu state
  selectedGeoLayer: DEFAULT_GEO_CATEGORY,
  selectedRegionDescriptor: undefined,
};

const explorerSlice = createSlice({
  name: 'explorer',
  initialState,
  reducers: {
    requestTaxonomy(state) {
      state.taxonomyIsLoading = true;
    },
    loadTaxonomy(state, action: PayloadAction<Taxonomy>) {
      state.taxonomy = action.payload;
      state.taxonomyIsLoading = false;
      state.taxonomyLoadError = undefined;
    },
    failTaxonomyRequest(state, action: PayloadAction<string>) {
      state.taxonomyIsLoading = false;
      state.taxonomyLoadError = action.payload;
    },

    requestRegionDetails(state, action: PayloadAction<RegionDescriptor>) {
      state.currentRegionIsLoading = true;
    },
    loadRegionDetails(state, action: PayloadAction<Region>) {
      state.currentRegion = action.payload;
      state.currentRegionIsLoading = false;
      state.currentRegionLoadError = undefined;
    },
    failRegionDetailsRequest(state, action: PayloadAction<string>) {
      state.currentRegion = undefined;
      state.currentRegionIsLoading = false;
      state.currentRegionLoadError = action.payload;
    },

    // menu slices
    selectGeoLayer(state, action: PayloadAction<GeoLayer>) {
      state.selectedGeoLayer = action.payload;
    },
    selectRegion(state, action: PayloadAction<RegionDescriptor>) {
      state.selectedRegionDescriptor = action.payload;
    },
  },
});

export const { actions, reducer, name: sliceKey } = explorerSlice;
