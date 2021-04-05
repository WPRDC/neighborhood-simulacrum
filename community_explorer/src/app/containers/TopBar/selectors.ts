import { createSelector } from '@reduxjs/toolkit';

import { RootState } from 'types';
import { initialState } from './slice';

const selectDomain = (state: RootState) => state.topBar || initialState;

export const selectTopBar = createSelector(
  [selectDomain],
  topBarState => topBarState,
);

export const selectColorMode = createSelector(
  [selectTopBar],
  topBarState => topBarState.colorMode,
);
