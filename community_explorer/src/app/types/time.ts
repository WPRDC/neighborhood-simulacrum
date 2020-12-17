/*
 *
 * Series types
 *
 */
import { Described } from './common';

export type Time = YearSeries; // union any more new series

export enum SeriesResourceType {
  YearSeries = 'YearSeries',
}

export interface SeriesBase extends Described {
  resourcetype: SeriesResourceType;
}

export interface YearSeries extends SeriesBase {
  year: number;
  resourcetype: SeriesResourceType.YearSeries;
}

export interface TimePart {
  slug: string;
  name: string;
  time_point: Date;
  time_unit: number;
}

export interface TimeAxis extends Described {
  unit: number;
  timeParts: TimePart[];
}

export interface StaticTimeAxis extends TimeAxis {
  dates: Date[];
  start: Date;
  end: Date;
}

export interface StaticConsecutiveTimeAxis extends TimeAxis {
  start: Date;
  end: Date;
  ticks: number;
}

export interface RelativeTimeAxis extends TimeAxis {
  startOffset: number;
  ticks: number;
  direction: number;
}
