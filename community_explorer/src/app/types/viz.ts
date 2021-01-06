/*
 *
 * Data Viz types
 *
 */

import { Datum, Described } from './common';
import { TimeAxis } from './time';
import { Variable } from './variable';

export type DataVizID = Described;

export type DataVisualization =
  | TableViz
  | PieChartViz
  | MiniMapViz
  | SentenceViz
  | BigValueViz;

export enum DataVizResourceType {
  Table = 'Table',
  PieChart = 'PieChart',
  MiniMap = 'MiniMap',
  Sentence = 'Sentence',
  BigValue = 'BigValue',
}

type DataVizDataPointPart<T = string> = 'v' | 'm' | T; // v - value; m - margin o' error

export type DataVizDataPoint = Record<DataVizDataPointPart, any>;

// Response data formats
export type TableData = Record<string, DataVizDataPoint>[];
export type ChartData = Record<string, DataVizDataPoint>[];
export type MapData = any;
export type SentenceData = string;
export type BigValueData = DataVizDataPoint;

export type DataVizData =
  | TableData
  | ChartData
  | MapData
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

export interface MiniMapViz extends DataVizBase {
  data?: MapData;
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

export interface DataVizBase extends Described {
  timeAxis: TimeAxis;
  variables: Variable[];
  resourcetype: DataVizResourceType;
}
