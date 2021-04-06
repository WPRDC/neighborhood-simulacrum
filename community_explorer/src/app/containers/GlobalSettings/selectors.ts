import { createSelector } from '@reduxjs/toolkit';

import { RootState } from 'types';
import { initialState } from './slice';

const selectDomain = (state: RootState) => state.globalSettings || initialState;

export const selectGlobalSettings = createSelector(
  [selectDomain],
  globalSettingsState => globalSettingsState,
);

export const selectColorMode = createSelector(
  [selectGlobalSettings],
  topBarState => topBarState.colorMode,
);
