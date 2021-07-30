import React from 'react';
import {
  TabularData,
  ChartViz,
  DataVizBase,
  DataVizID,
  DataVizType,
  Downloaded,
  GeogIdentifier,
  MiniMapOptions,
  MiniMapViz,
  TableViz,
  Variable,
  VizProps,
  RowRecord,
} from '../../types';
import { saveAs } from 'file-saver';
import { Table } from '../../data-vizes/Table';
import { Sentence } from '../../data-vizes/Sentence';
import BigValue from '../../data-vizes/BigValue';
import { MiniMap } from '../../data-vizes/MiniMap';
import { Text } from '@react-spectrum/text';
import { PlainObject } from 'react-vega';
import { DataVizVariant } from './types';
import { DataVizMini } from '../../components/DataVizMini';
import { DataVizPreview } from '../../components/DataVizPreview';
import { DataVizCard } from '../../components/DataVizCard';
import { dumpCSV } from '../../util';
import { DataVizDetails } from '../../components/DataVizDetails';
import { MissingVizMessage } from '../../components/MissingVizMessage';
import { BarChart } from '../../data-vizes/BarChart';

export function getSpecificDataViz(
  dataViz?: Downloaded<DataVizBase>,
  error?: string,
) {
  console.log({ dataViz, error });
  if (!!error) return MissingVizMessage;
  console.log(error);
  if (!dataViz) return undefined;

  const componentMap: Record<DataVizType, React.FC<VizProps<any, any>>> = {
    [DataVizType.Table]: Table,
    [DataVizType.Chart]: BarChart, // fixme: make a generic chart viz
    [DataVizType.MiniMap]: MiniMap,
    [DataVizType.BigValue]: BigValue,
    [DataVizType.Sentence]: Sentence,
  };
  return componentMap[dataViz.vizType];
}

export function makeKey(dataVizID: DataVizID, geogIdentifier: GeogIdentifier) {
  return `${dataVizID.slug}@${geogIdentifier.geogType}/${geogIdentifier.geogID}`;
}

/**
 * Formats `value` for `variable` per styling data extracted from `variable`.
 * @param {Variable} variable
 * @param {number} value
 */
export function formatValue(
  variable: Variable,
  value?: string | number | Date,
): React.ReactNode {
  switch (typeof value) {
    case 'string':
      return value;
    case 'number':
    case 'object':
      return value.toLocaleString(
        undefined,
        variable.localeOptions || undefined,
      );
    default:
      return 'N/A';
  }
}

/**
 * Formats a percent value to site standards
 * @param {number} value
 */
export function formatPercent(value?: number): React.ReactNode {
  if (typeof value === 'number')
    return value.toLocaleString(undefined, {
      style: 'percent',
      minimumSignificantDigits: 1,
      maximumSignificantDigits: 3,
    });
  return 'N/A';
}

/**
 * Extracts title  from `Variable` and formats it.
 * @param {Variable} variable
 */
export function formatCategory(variable: Variable): React.ReactNode {
  const dashes = Array(variable.depth).join('-');
  let category;
  if (!!variable.shortName)
    category = <abbr title={variable.name}>{variable.shortName}</abbr>;
  else category = variable.name;
  return (
    <Text>
      {!!dashes && `${dashes} `}
      {category}
    </Text>
  );
}

/**
 * Copies and adds human-friendly labels to the tabular data provided from
 * the API and wraps it in the format Vega accepts.
 *
 * @param dataViz
 */
export function prepDataForVega(
  dataViz: Downloaded<ChartViz, TabularData>,
): PlainObject {
  // todo: make lookup table for the labels and toss that into the vega spec!

  const addLabels = makeLabeler(dataViz);
  return { table: dataViz.data.map(addLabels) };
}

/**
 * Returns a function that extracts human-readable labels from `dataViz`.
 * @param {DataVizBase} dataViz - dataViz definition object
 */
const makeLabeler = (dataViz: DataVizBase) => (datum: RowRecord) => {
  // todo: memoize these lookups
  const variable = dataViz.variables.find(v => v.slug === datum.variable);
  const time = dataViz.timeAxis.timeParts.find(t => t.slug === datum.time);

  const variableLabel = variable ? variable.name : datum.variable;
  const timeLabel = time ? time.name : datum.time;

  return { ...datum, variableLabel, timeLabel };
};

/**
 * Returns the DataViz component based on the supplied variant.
 *
 * @param {DataVizVariant} variant
 */
export function getVariantComponent(variant: DataVizVariant) {
  switch (variant) {
    case DataVizVariant.Blurb:
      return DataVizMini;
    case DataVizVariant.Preview:
      return DataVizPreview;
    case DataVizVariant.Details:
      return DataVizDetails;
    case DataVizVariant.Default:
    default:
      return DataVizCard;
  }
}

export function downloadCSV(dataViz: Downloaded<DataVizBase>) {
  switch (dataViz.vizType) {
    case DataVizType.Table:
      return downloadTable(dataViz as Downloaded<TableViz, TabularData>);
    case DataVizType.Chart:
      return downloadChart(dataViz as Downloaded<ChartViz, TabularData>);
    case DataVizType.MiniMap:
      return downloadMiniMap(dataViz as Downloaded<MiniMapViz, MiniMapOptions>);
  }
}

export function downloadTable(table: Downloaded<TableViz, TabularData>): void {
  const blob = new Blob([dumpCSV(table.data)]);
  const fileName = `${table.slug}-${table.geog.title.replace(
    RegExp('s+'),
    '-',
  )}`;
  saveAs(blob, fileName);
}

export function downloadChart(chart: Downloaded<ChartViz, TabularData>): void {
  const blob = new Blob([dumpCSV(chart.data)], {
    type: 'text/csv;charset=utf-8',
  });
  const fileName = `${chart.slug}-${chart.geog.title}.csv`;
  saveAs(blob, fileName);
}

export function downloadMiniMap(
  map: Downloaded<MiniMapViz, MiniMapOptions>,
): void {
  const urls: string[] = map.data.sources
    .filter(s => typeof s.data === 'string')
    .map(s => s.data as string);
  const fileName = `${map.slug}.geojson?format=json`;
  const url = urls[0] + '?download=true';
  saveAs(url, fileName);
}
