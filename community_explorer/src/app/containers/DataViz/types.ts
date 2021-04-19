import {
  DataVizBase,
  DataVizData,
  DataVizID,
  Downloaded,
  GeogIdentifier,
  VizMenuItem,
} from '../../types';
import React from 'react';

export interface DataVizState {
  dataVizDataCache: DataVizDataCache;
  // dataVizMetadataCache: Record<string, DataVisualization>;
}

/** Data and state of its collection for some dataviz at some geog*/
export interface DataVizDataRecord<
  T extends DataVizBase = DataVizBase,
  D extends DataVizData = DataVizData
> {
  dataViz: Downloaded<T, D>;
  isLoading: boolean;
  error?: string;
}

export type DataVizDataCache = Record<string, DataVizDataRecord>;

export interface DataVizRequest {
  dataVizID: DataVizID;
  geogIdentifier: GeogIdentifier;
}

export type ContainerState = DataVizState;

export enum DataVizVariant {
  Default,
  Preview,
  Blurb,
  Details,
}

export interface MenuItem {
  key: VizMenuItem;
  label: React.ReactNode;
  icon?: React.ReactNode;
}

export enum AvailableDialogs {
  Report,
  Share,
}
