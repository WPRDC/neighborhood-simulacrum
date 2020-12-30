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

export const selectCurrentRegion = createSelector(
  [selectExplorer],
  explorerState => explorerState.currentRegion,
);

export const selectCurrentRegionIsLoading = createSelector(
  [selectExplorer],
  explorerState => explorerState.currentRegionIsLoading,
);

export const selectCurrentRegionLoadError = createSelector(
  [selectExplorer],
  explorerState => explorerState.currentRegionLoadError,
);

export const selectSelectedGeoLayer = createSelector(
  [selectExplorer],
  explorerState => explorerState.selectedGeoLayer,
);

export const selectSelectedRegionDescriptor = createSelector(
  [selectExplorer],
  explorerState => explorerState.selectedRegionDescriptor,
);
