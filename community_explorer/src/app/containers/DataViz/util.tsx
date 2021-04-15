import React from 'react';

import {
  ChartData,
  DataVizBase,
  DataVizData,
  DataVizID,
  DataVizResourceType,
  Downloaded,
  GeogIdentifier,
  Variable,
  VizProps,
} from '../../types';

import { Table } from '../../data-vizes/Table';
import { PieChart } from '../../data-vizes/PieChart';
import { Sentence } from '../../data-vizes/Sentence';
import BigValue from '../../data-vizes/BigValue';
import { BarChart } from '../../data-vizes/BarChart';
import { LineChart } from '../../data-vizes/LineChart';
import { MiniMap } from '../../data-vizes/MiniMap';
import { Text } from '@react-spectrum/text';
import { PlainObject } from 'react-vega';

export function getSpecificDataViz(
  dataViz?: Downloaded<DataVizBase>,
) {
  if (!dataViz) return undefined;

  const componentMap: Record<
    DataVizResourceType,
    React.FC<VizProps<any, any>>
  > = {
    [DataVizResourceType.Sentence]: Sentence,
    [DataVizResourceType.BigValue]: BigValue,
    [DataVizResourceType.MiniMap]: MiniMap,
    [DataVizResourceType.Table]: Table,
    [DataVizResourceType.PieChart]: PieChart,
    [DataVizResourceType.LineChart]: LineChart,
    [DataVizResourceType.BarChart]: BarChart,
  };
  return componentMap[dataViz.resourcetype];
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
 * Formats a percent value per site standards
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
 * Copies the tabular data provided from the API and wraps it in the format `Vega` accepts.
 * @param {ChartData} data - the tabular data from the viz API
 */
export function prepDataForVega(data: ChartData): PlainObject {
  return { table: data.map(datum => ({ ...datum })) };
}

// export function downloadTable(table: Downloaded<TableViz, TableData>): void {
//   const blob = new Blob([
//     dumpCSV(
//       table.data.map(record =>
//         Object.entries(record).reduce((a, [k, v]) => ({ ...a, k: v.v }), {}),
//       ),
//     ),
//   ]);
//   const fileName = `${table.slug}-${table.geog.title.replace(
//     RegExp('s+'),
//     '-',
//   )}`;
//   saveAs(blob, fileName);
// }
//
// export function downloadChart(chart: Downloaded<ChartViz, ChartData>): void {
//   const blob = new Blob([dumpCSV(chart.data)], {
//     type: 'text/csv;charset=utf-8',
//   });
//   const fileName = `${chart.slug}-${chart.geog.title}.csv`;
//   saveAs(blob, fileName);
// }
//
// export function downloadMiniMap(
//   map: Downloaded<MiniMapViz, MiniMapData>,
// ): void {
//   const urls: string[] = map.data.sources
//     .filter(s => typeof s.data === 'string')
//     .map(s => s.data as string);
//   const fileName = `${map.slug}.geojson?format=json`;
//
//   const a = document.createElement('a');
//   a.href = urls[0] + '?download=true';
//   a.download = fileName;
//   a.target = '_blank';
//   a.rel = 'noreferrer';
//   document.body.appendChild(a);
//   a.click();
//   document.body.removeChild(a);
// }
