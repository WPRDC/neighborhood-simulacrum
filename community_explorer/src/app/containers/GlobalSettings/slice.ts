import { PayloadAction } from '@reduxjs/toolkit';
import { createSlice } from 'utils/@reduxjs/toolkit';
import { ContainerState } from './types';
import { ColorMode } from '../../types';

const DEFAULT_COLOR_MODE: ColorMode = ColorMode.Light;
// window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
//   ? ColorMode.Dark
//   : ColorMode.Light;

export const initialState: ContainerState = {
  colorMode: DEFAULT_COLOR_MODE,
};

const globalSettingsSlice = createSlice({
  name: 'globalSettings',
  initialState,
  reducers: {
    changeColorMode(state, action: PayloadAction<ColorMode>) {
      state.colorMode = action.payload;
    },
  },
});

export const { actions, reducer, name: sliceKey } = globalSettingsSlice;
