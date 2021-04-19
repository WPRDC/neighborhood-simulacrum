/*
 *
 * Data Viz types
 *
 */

import { Described } from './common';
import { TimeAxis } from './time';
import { VizVariable } from './variable';
import { SourceProps } from 'react-map-gl';
import { LayerOptions, LegendProps, MapProps } from 'wprdc-components';
import { ColorMode, GeogDescriptor, GeogIdentifier, SourceBase } from './index';
import React, { PropsWithChildren } from 'react';

export interface DataVizID extends Described {
  viewHeight: number;
  viewWidth: number;
  resourcetype: DataVizResourceType;
}

export interface DataVizBase extends DataVizID {
  timeAxis: TimeAxis;
  variables: VizVariable[];
  resourcetype: DataVizResourceType;
  sources: SourceBase[];
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

export type ChartViz = LineChartViz | BarChartViz | PieChartViz;

// Response data formats
export type TableData = Record<string, DataVizDataPoint>[];

export interface ChartRecord extends Record<string, string | number | boolean> {
  variable: string;
  timeSeries: string;
  geog: string;
  value: number;
}

export type ChartData = ChartRecord[];

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

/** DataViz type T with `data` required */
export type Downloaded<T extends DataVizBase, D = DataVizData> = T & {
  data: D;
  geog: GeogDescriptor;
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
  layout: 'bar' | 'column';
  acrossGeogs: boolean;
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

export interface VizProps<T extends DataVizBase, D extends DataVizData>
  extends PropsWithChildren<any> {
  dataViz: Downloaded<T, D>;
  geog: GeogIdentifier;
  colorScheme?: ColorMode;
  vizHeight?: number;
  vizWidth?: number;
}

export interface VizWrapperProps {
  isLoading: boolean;
  geogIdentifier: GeogIdentifier;
  colorScheme: ColorMode;
  dataViz?: Downloaded<DataVizBase>;
  CurrentViz?: React.FC<VizProps<DataVizBase, DataVizData>>;
  menu: JSX.Element;
}

export enum VizMenuItem {
  DownloadData = 'DownloadData',
  DownloadSVG = 'DownloadSvg',
  Report = 'Report',
  Share = 'Share',
}
