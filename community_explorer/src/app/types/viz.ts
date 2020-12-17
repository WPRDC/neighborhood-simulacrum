/*
 *
 * Data Viz types
 *
 */

import { Described } from './common';
import { TimeAxis } from './time';
import { Variable } from './variable';

export type DataVizID = Described;

export type DataVisualization = TableViz | PieChartViz | MiniMapViz;

export enum DataVizResourceType {
  Table = 'Table',
  PieChart = 'PieChart',
  MiniMap = 'MiniMap',
  DataViz = 'DataViz', // todo: ensure that this can be removed.  backend shouldn't share any dataviz's without a type
}

type DataVizDataPointPart = 'v' | 'm' | string; // v - value; m - margin o' error

export type DataVizDataPoint = Record<DataVizDataPointPart, any>;

export type TableData = Record<string, DataVizDataPoint>[];
export type ChartData = Record<string, DataVizDataPoint>[];
export type MapData = any;

export type DataVizData = TableData | ChartData | MapData;

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

export interface DataVizBase extends Described {
  timeAxis: TimeAxis;
  variables: Variable[];
  resourcetype: DataVizResourceType;
}
