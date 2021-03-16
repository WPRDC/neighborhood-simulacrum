import {
  DataVizID,
  DataVizData,
  RegionDescriptor,
  DataVizBase,
  Downloaded,
  // DataVisualization,
} from '../../types';

export interface DataVizState {
  dataVizDataCache: DataVizDataCache;
  // dataVizMetadataCache: Record<string, DataVisualization>;
}

/** Data and state of its collection for some dataviz at some region*/
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
  regionDescriptor: RegionDescriptor;
}

export type ContainerState = DataVizState;

export enum DataVizAction {
  Share = 'share',
  Download = 'download',
  Embed = 'embed',
}
