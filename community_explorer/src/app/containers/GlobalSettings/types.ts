import { ColorMode } from 'app/types';

/* --- STATE --- */
export interface GlobalSettingsState {
  colorMode: ColorMode;
}

export type ContainerState = GlobalSettingsState;
