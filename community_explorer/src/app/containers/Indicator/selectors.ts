import { createSelector } from '@reduxjs/toolkit';

import { RootState } from 'types';
import { initialState } from './slice';

const selectDomain = (state: RootState) => state.indicator || initialState;

export const selectIndicator = createSelector(
  [selectDomain],
  indicatorState => indicatorState,
);
