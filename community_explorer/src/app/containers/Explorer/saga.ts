import { all, call, put, select, takeLatest } from 'redux-saga/effects';
import { PayloadAction } from '@reduxjs/toolkit';

import Api from '../../api';

import { actions } from './slice';
import { GeogDescriptor, GeogIdentifier, GeographyType } from '../../types';
import {
  selectGeogsListRecord,
  selectGeogsListsAreLoadingRecord,
} from './selectors';
import { GeogTypeDescriptor } from './types';

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

function* handleFetchGeoLayers(/* action */) {
  try {
    const response = yield call(Api.requestGeoLayers);
    if (response.ok) {
      const data = yield response.json();
      yield put(actions.loadGeoLayers(data));
      yield put(actions.selectGeoType(data[3]));
    } else {
      yield put(actions.failGeoLayersRequest(response.text));
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn(err);
    yield put(actions.failGeoLayersRequest(err.toString()));
  }
}

function* handleFetchGeogDescription(action: PayloadAction<GeogIdentifier>) {
  const geogIdentifier = action.payload;
  try {
    const response = yield call(Api.requestGeogDescription, geogIdentifier);
    if (response.ok) {
      const data = yield response.json();
      yield put(actions.loadGeogDetails(data));
    } else {
      yield put(actions.failGeogDetailsRequest(response.text));
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn(err);
    yield put(actions.failGeogDetailsRequest(err.toString()));
  }
}

function* checkGeogListCache(action: PayloadAction<GeogTypeDescriptor>) {
  console.debug('checking cache');
  const geogType = action.payload.id;
  const geogsListRecord = yield select(selectGeogsListRecord);
  const loadingRecord = yield select(selectGeogsListsAreLoadingRecord);
  // on cache miss, request from backend.
  if (!geogsListRecord[geogType] && !loadingRecord[geogType]) {
    yield put(actions.requestGeogsForLayer(geogType));
  }
}

function* handleFetchGeogsForLayer(action: PayloadAction<GeographyType>) {
  const geogType = action.payload;
  try {
    const response = yield call(Api.requestGeogList, geogType);
    if (response.ok) {
      const geogs: GeogDescriptor[] = yield response.json();
      yield put(actions.loadGeogsForLayer({ geogType, geogs }));
    } else {
      yield put(actions.failLoadingGeogsForLayer(geogType));
    }
  } catch (err) {
    console.warn(err);
    yield put(actions.failLoadingGeogsForLayer(geogType));
  }
}

export function* explorerSaga() {
  yield all([
    takeLatest(actions.requestTaxonomy.type, handleFetchTaxonomy),
    takeLatest(actions.requestGeoLayers.type, handleFetchGeoLayers),
    takeLatest(actions.requestGeogDetails.type, handleFetchGeogDescription),
    takeLatest(actions.selectGeoType.type, checkGeogListCache),
    takeLatest(actions.requestGeogsForLayer, handleFetchGeogsForLayer),
  ]);
}
