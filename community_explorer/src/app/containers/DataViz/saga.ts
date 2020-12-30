import { call, put, takeEvery } from 'redux-saga/effects';
import { actions } from './slice';

import { DataVizRequest } from './types';
import Api from '../../api';
import { PayloadAction } from '@reduxjs/toolkit';

function* handleRequestDataVizData(action: PayloadAction<DataVizRequest>) {
  const { dataVizID, regionDescriptor } = action.payload;
  try {
    const response: Response = yield call(
      Api.requestDataViz,
      dataVizID,
      regionDescriptor,
    );

    if (response.ok) {
      const data = yield response.json();
      if (data.error.level) {
        console.warn(data.error.message);
        yield put(
          actions.dataVizRequestError({
            dataVizID,
            regionDescriptor,
            errorMsg: data.error.message,
          }),
        );
      } else {
        yield put(actions.loadDataViz({ dataVizID, regionDescriptor, data }));
      }
    } else {
      console.warn(response.statusText);
      yield put(
        actions.dataVizRequestError({
          dataVizID,
          regionDescriptor,
          errorMsg: response.statusText,
        }),
      );
    }
  } catch (err) {
    console.warn(err);
    yield put(
      actions.dataVizRequestError({
        dataVizID,
        regionDescriptor,
        errorMsg: err.toString(),
      }),
    );
  }
}

export function* dataVizSaga() {
  yield takeEvery(actions.requestDataViz.type, handleRequestDataVizData);
}
