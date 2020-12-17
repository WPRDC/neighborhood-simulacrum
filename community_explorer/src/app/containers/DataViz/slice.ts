import { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from 'utils/@reduxjs/toolkit';
import {
  ContainerState,
  DataVizDataCache,
  DataVizDataRecord,
  DataVizRequest,
} from './types';
import { makeKey } from './util';
import { DataVizData, DataVizID, RegionID } from '../../types';

// The initial state of the DataViz container
export const initialState: ContainerState = {
  dataVizDataCache: {},
  // dataVizMetadataCache: {},
};

/**
 * Updated data cache record for dataViz with id dataVizID at region
 * @param cache
 * @param dataVizID
 * @param region
 * @param update
 */
function updateData(
  cache: DataVizDataCache,
  dataVizID: DataVizID,
  regionID: RegionID,
  update: Partial<DataVizDataRecord<Partial<DataVizData>>>,
) {
  const key = makeKey(dataVizID, regionID);
  return Object.assign({}, cache, {
    [key]: update,
  });
}

const dataVizSlice = createSlice({
  name: 'dataViz',
  initialState,
  reducers: {
    requestDataViz(state, action: PayloadAction<DataVizRequest>) {
      const { dataVizID, regionID } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        regionID,
        {
          isLoading: true,
          error: undefined,
        },
      );
    },
    loadDataViz(state, action: PayloadAction<DataVizRequest & { data: any }>) {
      const { dataVizID, regionID, data } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        regionID,
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
      const { dataVizID, regionID, errorMsg } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        regionID,
        {
          isLoading: false,
          error: errorMsg,
        },
      );
    },
  },
});

export const { actions, reducer, name: sliceKey } = dataVizSlice;
