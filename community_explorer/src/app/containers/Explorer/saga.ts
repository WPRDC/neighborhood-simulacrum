import { all, call, put, takeLatest } from 'redux-saga/effects';
import { PayloadAction } from '@reduxjs/toolkit';

import Api from '../../api';

import { actions } from './slice';
import { RegionID } from '../../types';

function* handleFetchTaxonomy(/* action */) {
  try {
    const response = yield call(Api.requestTaxonomy);
    if (response.ok) {
      const data = yield response.json();
      yield put(actions.loadTaxonomy(data));
    } else {
      yield put(actions.failTaxonomyRequest(response.text));
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn(err);
    yield put(actions.failTaxonomyRequest(err.toString()));
  }
}

function* handleFetchRegionDescription(action: PayloadAction<RegionID>) {
  const regionID = action.payload;
  try {
    const response = yield call(Api.requestRegionDescription, regionID);
    if (response.ok) {
      const data = yield response.json();
      yield put(actions.loadRegionDetails(data));
    } else {
      yield put(actions.failRegionDetailsRequest(response.text));
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn(err);
    yield put(actions.failRegionDetailsRequest(err.toString()));
  }
}

export function* explorerSaga() {
  yield all([
    takeLatest(actions.requestTaxonomy.type, handleFetchTaxonomy),
    takeLatest(actions.requestRegionDetails.type, handleFetchRegionDescription),
  ]);
}
