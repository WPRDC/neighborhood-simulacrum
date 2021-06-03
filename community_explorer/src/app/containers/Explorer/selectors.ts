import { createSelector } from '@reduxjs/toolkit';

import { RootState } from 'types';
import { initialState } from './slice';

const selectDomain = (state: RootState) => state.explorer || initialState;

export const selectExplorer = createSelector(
  [selectDomain],
  explorerState => explorerState,
);

export const selectTaxonomy = createSelector(
  [selectExplorer],
  explorerState => explorerState.taxonomy,
);

export const selectTaxonomyIsLoading = createSelector(
  [selectExplorer],
  explorerState => explorerState.taxonomyIsLoading,
);

export const selectTaxonomyLoadError = createSelector(
  [selectExplorer],
  explorerState => explorerState.taxonomyLoadError,
);

export const selectGeoLayers = createSelector(
  [selectExplorer],
  explorerState => explorerState.geoLayers,
);

export const selectGeoLayersIsLoading = createSelector(
  [selectExplorer],
  explorerState => explorerState.geoLayersIsLoading,
);

export const selectGeoLayersLoadError = createSelector(
  [selectExplorer],
  explorerState => explorerState.geoLayersLoadError,
);

export const selectCurrentGeog = createSelector(
  [selectExplorer],
  explorerState => explorerState.currentGeog,
);

export const selectCurrentGeogIsLoading = createSelector(
  [selectExplorer],
  explorerState => explorerState.currentGeogIsLoading,
);

export const selectCurrentGeogLoadError = createSelector(
  [selectExplorer],
  explorerState => explorerState.currentGeogLoadError,
);

export const selectSelectedGeoLayer = createSelector(
  [selectExplorer],
  explorerState => explorerState.selectedGeoLayer,
);

export const selectSelectedGeogIdentifier = createSelector(
  [selectExplorer],
  explorerState => explorerState.selectedGeogIdentifier,
);

export const selectGeogsListRecord = createSelector(
  [selectExplorer],
  explorerState => explorerState.geogsListsRecord,
);

export const selectGeogsListsAreLoadingRecord = createSelector(
  [selectExplorer],
  explorerState => explorerState.geogsListsAreLoadingRecord,
);
