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

import { Column } from 'react-table';

export interface DataVizID extends Described {
  vizType: DataVizType;
  staticOptions: Record<string, any>;
}

export interface DataVizBase extends DataVizID {
  timeAxis: TimeAxis;
  variables: VizVariable[];
  sources: SourceBase[];
}

export type DataVisualization =
  | TableViz
  | MiniMapViz
  | SentenceViz
  | BigValueViz;

export enum DataVizType {
  Table = 'Table',
  Chart = 'Chart',
  MiniMap = 'MiniMap',
  Sentence = 'Sentence',
  BigValue = 'BigValue',
}

export interface RowRecord {
  variable: string;
  geog: string;
  time: string;
  value: number;
  moe?: number;
  percent?: number;
  denom?: number;
}

export interface LabeledRowRecord {
  variable: string;
  variableLabel: string;
  geog: string;
  time: string;
  timeLabel: string;
  value: number;
  moe?: number;
  percent?: number;
  denom?: number;
}

export type TabularData = RowRecord[];

export interface TableDatum {
  value: number | string;
  moe?: number;
  percent?: number;
  denom?: number;
}

export type TableRecord = Record<string, TableDatum> & {
  variable: string;
};

export type TableData = TableRecord[];

export type MiniMapOptions = {
  sources: SourceProps[];
  layers: LayerOptions[];
  mapOptions: Partial<MapProps>;
  legends: LegendProps[];
  localeOptions?: Partial<Intl.NumberFormatOptions>;
};

export type DataVizData = TabularData | MiniMapOptions | TableData;

export interface ErrorRecord {
  status: string;
  level: number;
  message?: string;
}

/** DataViz type T with `data` required */
export type Downloaded<
  T extends DataVizBase,
  D = DataVizData,
  O = Record<string, any>
> = T & {
  data: D;
  options: O;
  error: ErrorRecord;
  geog: GeogDescriptor;
};

export interface TableViz extends DataVizBase {
  data?: TableData;
  vizType: DataVizType.Table;
}

export interface ChartViz extends DataVizBase {
  data?: TabularData;
  vizType: DataVizType.Chart;
}

export interface MiniMapViz extends DataVizBase {
  options?: MiniMapOptions;
  vizType: DataVizType.MiniMap;
}

export interface SentenceViz extends DataVizBase {
  data?: TabularData;
  vizType: DataVizType.Sentence;
}

export interface BigValueViz extends DataVizBase {
  data?: TabularData;
  vizType: DataVizType.BigValue;
}

export interface TableOptions {
  transpose: boolean;
  showPercent: boolean;
  columns: Column[];
}

export type VizProps<
  T extends DataVizBase,
  D extends DataVizData
> = PropsWithChildren<{
  dataViz: Downloaded<T, D>;
  geog: GeogIdentifier;
  colorScheme?: ColorMode;
  vizHeight?: number;
  vizWidth?: number;
  error?: string;
}>;

export interface VizWrapperProps {
  isLoading: boolean;
  error?: string;
  geogIdentifier?: GeogIdentifier;
  colorScheme: ColorMode;
  menu: JSX.Element;
  dataViz?: Downloaded<DataVizBase>;
  CurrentViz?: React.FC<VizProps<DataVizBase, DataVizData>>;
  breadcrumbs?: JSX.Element[];
  onExplore?: () => void;
  onBreadcrumbClick?: (path: React.ReactText) => void;
}

export enum VizMenuItem {
  DownloadData = 'DownloadData',
  DownloadSVG = 'DownloadSvg',
  Report = 'Report',
  Share = 'Share',
  API = 'API',
}
