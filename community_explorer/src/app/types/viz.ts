/*
 *
 * Data Viz types
 *
 */

import { Datum, Described } from './common';
import { TimeAxis } from './time';
import { Variable } from './variable';
import { LayerProps, SourceProps } from 'react-map-gl';
import {
  LayerOptions,
  LegendOptions,
  LegendProps,
  MapProps,
} from 'wprdc-components';

export interface DataVizID extends Described {
  viewHeight: number;
  viewWidth: number;
}

export interface DataVizBase extends DataVizID {
  timeAxis: TimeAxis;
  variables: Variable[];
  resourcetype: DataVizResourceType;
}

export type DataVisualization =
  | TableViz
  | PieChartViz
  | BarChartViz
  | LineChartViz
  | MiniMapViz
  | SentenceViz
  | BigValueViz;

export enum DataVizResourceType {
  Table = 'Table',
  PieChart = 'PieChart',
  BarChart = 'BarChart',
  LineChart = 'LineChart',
  MiniMap = 'MiniMap',
  Sentence = 'Sentence',
  BigValue = 'BigValue',
}

type DataVizDataPointPart<T = string> = 'v' | 'm' | T; // v - value; m - margin o' error

export type DataVizDataPoint = Record<DataVizDataPointPart, any>;

// Response data formats
export type TableData = Record<string, DataVizDataPoint>[];
export type ChartData = Record<string, DataVizDataPoint>[];
export type MiniMapData = {
  sources: SourceProps[];
  layers: LayerOptions[];
  mapOptions: Partial<MapProps>;
  legends: LegendProps[];
};
export type SentenceData = string;

export interface BigValueDataPoint {
  v: any;
  options: Record<string, any>;
}

export type BigValueData = [BigValueDataPoint];

export type DataVizData =
  | TableData
  | ChartData
  | MiniMapData
  | SentenceData
  | BigValueData;

/** T with `data` required */
export type Downloaded<T extends DataVizBase, D extends DataVizData> = T & {
  data: D;
};

export interface TableViz extends DataVizBase {
  data?: TableData;
  resourcetype: DataVizResourceType.Table;
}

export interface PieChartViz extends DataVizBase {
  data?: ChartData;
  resourcetype: DataVizResourceType.PieChart;
}

export interface BarChartViz extends DataVizBase {
  data?: ChartData;
  resourcetype: DataVizResourceType.BarChart;
}

export interface LineChartViz extends DataVizBase {
  data?: ChartData;
  resourcetype: DataVizResourceType.LineChart;
}

export interface MiniMapViz extends DataVizBase {
  data?: MiniMapData;
  resourcetype: DataVizResourceType.MiniMap;
}

export interface SentenceViz extends DataVizBase {
  text: string;
  sentence_parts: string[];
  data?: SentenceData;
  resourcetype: DataVizResourceType.Sentence;
}

export interface BigValueViz extends DataVizBase {
  note?: string;
  data?: BigValueData;
  resourcetype: DataVizResourceType.BigValue;
}
