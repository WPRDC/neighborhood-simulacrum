import { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from 'utils/@reduxjs/toolkit';
import { ColorMode, ContainerState } from './types';

const DEFAULT_COLOR_MODE: ColorMode =
  window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
    ? ColorMode.Dark
    : ColorMode.Light;

// The initial state of the TopBar container
export const initialState: ContainerState = {
  colorMode: DEFAULT_COLOR_MODE,
};

const topBarSlice = createSlice({
  name: 'topBar',
  initialState,
  reducers: {
    changeColorMode(state, action: PayloadAction<ColorMode>) {
      state.colorMode = action.payload;
    },
  },
});

export const { actions, reducer, name: sliceKey } = topBarSlice;
