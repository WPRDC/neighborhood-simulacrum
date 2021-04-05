/* --- STATE --- */
export interface TopBarState {
  colorMode: ColorMode;
}

export enum ColorMode {
  Light = 'light',
  Dark = 'dark',
}

export type ContainerState = TopBarState;
