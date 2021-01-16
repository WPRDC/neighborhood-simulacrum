import {
  DataVizID,
  DataVizData,
  RegionDescriptor,
  // DataVisualization,
} from '../../types';

export interface DataVizState {
  dataVizDataCache: DataVizDataCache;
  // dataVizMetadataCache: Record<string, DataVisualization>;
}

/** Data and state of its collection for some dataviz at some region*/
export interface DataVizDataRecord<T extends DataVizData> {
  dataViz: T;
  isLoading: boolean;
  error?: string;
}

export type DataVizDataCache = Record<string, DataVizDataRecord<DataVizData>>;

export interface DataVizRequest {
  dataVizID: DataVizID;
  regionDescriptor: RegionDescriptor;
}

export type ContainerState = DataVizState;