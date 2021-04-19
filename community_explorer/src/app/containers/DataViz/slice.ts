import { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from 'utils/@reduxjs/toolkit';
import {
  ContainerState,
  DataVizDataCache,
  DataVizDataRecord,
  DataVizRequest,
} from './types';
import { downloadCSV, makeKey } from './util';
import {
  DataVizBase,
  DataVizID,
  Downloaded,
  GeogIdentifier,
} from '../../types';

// The initial state of the DataViz container
export const initialState: ContainerState = {
  dataVizDataCache: {},
  // dataVizMetadataCache: {},
};

/**
 * Updated data cache record for dataViz with id dataVizID at geog
 * @param cache
 * @param dataVizID
 * @param geogIdentifier
 * @param update
 */
function updateData(
  cache: DataVizDataCache,
  dataVizID: DataVizID,
  geogIdentifier: GeogIdentifier,
  update: Partial<DataVizDataRecord>,
) {
  const key = makeKey(dataVizID, geogIdentifier);
  return Object.assign({}, cache, {
    [key]: update,
  });
}

const dataVizSlice = createSlice({
  name: 'dataViz',
  initialState,
  reducers: {
    requestDataViz(state, action: PayloadAction<DataVizRequest>) {
      const { dataVizID, geogIdentifier } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        geogIdentifier,
        {
          isLoading: true,
          error: undefined,
        },
      );
    },
    loadDataViz(state, action: PayloadAction<DataVizRequest & { data: any }>) {
      const { dataVizID, geogIdentifier, data } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        geogIdentifier,
        {
          dataViz: data,
          isLoading: false,
          error: undefined,
        },
      );
    },
    dataVizRequestError(
      state,
      action: PayloadAction<DataVizRequest & { errorMsg: string }>,
    ) {
      const { dataVizID, geogIdentifier, errorMsg } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        geogIdentifier,
        {
          isLoading: false,
          error: errorMsg,
        },
      );
    },
    downloadDataVizData(state, action: PayloadAction<Downloaded<DataVizBase>>) {
      downloadCSV(action.payload);
    },
  },
});

export const { actions, reducer, name: sliceKey } = dataVizSlice;
