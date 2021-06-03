import { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from 'utils/@reduxjs/toolkit';
import { ContainerState, GeogLoadPayload, GeogTypeDescriptor } from './types';
import { Geog, GeogIdentifier, GeographyType, Taxonomy } from '../../types';

const EMPTY_GEOG_STORE = Object.values(GeographyType).reduce(
  (acc, cur) => ({ ...acc, [cur]: null }),
  {},
) as Record<GeographyType, any>;

// The initial state of the Explorer container
export const initialState: ContainerState = {
  taxonomy: undefined,
  taxonomyIsLoading: false,
  taxonomyLoadError: undefined,

  currentGeog: undefined,
  currentGeogIsLoading: false,
  currentGeogLoadError: undefined,

  // menu state
  geoLayers: undefined,
  geoLayersIsLoading: false,
  geoLayersLoadError: undefined,
  selectedGeoLayer: undefined,
  selectedGeogIdentifier: undefined,
  geogsListsRecord: EMPTY_GEOG_STORE,
  geogsListsAreLoadingRecord: EMPTY_GEOG_STORE,
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

    requestGeogDetails(state, action: PayloadAction<GeogIdentifier>) {
      state.currentGeogIsLoading = true;
    },
    loadGeogDetails(state, action: PayloadAction<Geog>) {
      state.currentGeog = action.payload;
      state.currentGeogIsLoading = false;
      state.currentGeogLoadError = undefined;
    },
    failGeogDetailsRequest(state, action: PayloadAction<string>) {
      state.currentGeog = undefined;
      state.currentGeogIsLoading = false;
      state.currentGeogLoadError = action.payload;
    },

    // menu slices
    requestGeoLayers(state) {
      state.geoLayersIsLoading = true;
    },
    loadGeoLayers(state, action: PayloadAction<GeogTypeDescriptor[]>) {
      state.geoLayersIsLoading = false;
      state.geoLayers = action.payload;
      state.selectedGeoLayer = action.payload.length
        ? action.payload[0]
        : undefined;
    },
    failGeoLayersRequest(state, action: PayloadAction<string>) {
      state.geoLayersIsLoading = false;
    },

    selectGeoType(state, action: PayloadAction<GeogTypeDescriptor>) {
      state.selectedGeoLayer = action.payload;
    },
    selectGeog(state, action: PayloadAction<GeogIdentifier>) {
      state.selectedGeogIdentifier = action.payload;
    },

    // requesting geography lists
    requestGeogsForLayer(state, action: PayloadAction<GeographyType>) {
      const geogType = action.payload;
      state.geogsListsAreLoadingRecord = Object.assign(
        {},
        state.geogsListsAreLoadingRecord,
        {
          [geogType]: true,
        },
      );
    },
    loadGeogsForLayer(state, action: PayloadAction<GeogLoadPayload>) {
      const { geogType, geogs } = action.payload;
      state.geogsListsAreLoadingRecord = Object.assign(
        {},
        state.geogsListsAreLoadingRecord,
        {
          [geogType]: false,
        },
      );
      state.geogsListsRecord = Object.assign({}, state.geogsListsRecord, {
        [geogType]: geogs,
      });
    },
    failLoadingGeogsForLayer(state, action: PayloadAction<GeographyType>) {
      state.geogsListsAreLoadingRecord = Object.assign(
        {},
        state.geogsListsAreLoadingRecord,
        {
          [action.payload]: false,
        },
      );
    },
  },
});

export const { actions, reducer, name: sliceKey } = explorerSlice;
