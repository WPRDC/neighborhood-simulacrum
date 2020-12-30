import { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from 'utils/@reduxjs/toolkit';
import {
  ContainerState,
  DataVizDataCache,
  DataVizDataRecord,
  DataVizRequest,
} from './types';
import { makeKey } from './util';
import { DataVizData, DataVizID, RegionDescriptor } from '../../types';

// The initial state of the DataViz container
export const initialState: ContainerState = {
  dataVizDataCache: {},
  // dataVizMetadataCache: {},
};

/**
 * Updated data cache record for dataViz with id dataVizID at region
 * @param cache
 * @param dataVizID
 * @param regionDescriptor
 * @param update
 */
function updateData(
  cache: DataVizDataCache,
  dataVizID: DataVizID,
  regionDescriptor: RegionDescriptor,
  update: Partial<DataVizDataRecord<Partial<DataVizData>>>,
) {
  const key = makeKey(dataVizID, regionDescriptor);
  return Object.assign({}, cache, {
    [key]: update,
  });
}

const dataVizSlice = createSlice({
  name: 'dataViz',
  initialState,
  reducers: {
    requestDataViz(state, action: PayloadAction<DataVizRequest>) {
      const { dataVizID, regionDescriptor } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        regionDescriptor,
        {
          isLoading: true,
          error: undefined,
        },
      );
    },
    loadDataViz(state, action: PayloadAction<DataVizRequest & { data: any }>) {
      const { dataVizID, regionDescriptor, data } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        regionDescriptor,
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
      const { dataVizID, regionDescriptor, errorMsg } = action.payload;
      state.dataVizDataCache = updateData(
        state.dataVizDataCache,
        dataVizID,
        regionDescriptor,
        {
          isLoading: false,
          error: errorMsg,
        },
      );
    },
  },
});

export const { actions, reducer, name: sliceKey } = dataVizSlice;
