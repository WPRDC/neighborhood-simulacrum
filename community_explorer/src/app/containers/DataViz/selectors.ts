import { createSelector } from '@reduxjs/toolkit';

import { RootState } from 'types';
import { initialState } from './slice';
import { selectSelectedGeogIdentifier } from '../Explorer/selectors';
import { makeKey } from './util';
import { DataVizID } from '../../types';

const selectDomain = (state: RootState) => state.dataViz || initialState;

// from old project
const selectDataVizDataCache = (state: RootState) =>
  selectDomain(state).dataVizDataCache;

const getDataVizDataKey: (
  state: RootState,
  props: { dataVizID: DataVizID },
) => string | undefined = (state, props) => {
  const geogIdentifier = selectSelectedGeogIdentifier(state);
  if (!geogIdentifier) return undefined;
  return makeKey(props.dataVizID, geogIdentifier);
};

const makeSelectDataVizData = () =>
  createSelector(
    selectDataVizDataCache,
    getDataVizDataKey,
    (dataVizDataCache, dataVizDataKey) => {
      if (dataVizDataCache && dataVizDataKey)
        return dataVizDataCache[dataVizDataKey];
      return undefined;
    },
  );

export { makeSelectDataVizData };
