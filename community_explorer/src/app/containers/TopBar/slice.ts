import { createSlice } from 'utils/@reduxjs/toolkit';
import { ContainerState } from './types';

// The initial state of the TopBar container
export const initialState: ContainerState = {};

const topBarSlice = createSlice({
  name: 'topBar',
  initialState,
  reducers: {},
});

export const { actions, reducer, name: sliceKey } = topBarSlice;
