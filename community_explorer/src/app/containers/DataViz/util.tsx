import React from 'react';

import {
  BarChartViz,
  BigValueData,
  BigValueViz,
  ChartData,
  DataVisualization,
  DataVizBase,
  DataVizData,
  DataVizDataPoint,
  DataVizID,
  DataVizResourceType,
  Downloaded,
  LineChartViz,
  MiniMapData,
  MiniMapViz,
  PieChartViz,
  RegionDescriptor,
  SentenceData,
  SentenceViz,
  TableData,
  TableViz,
  Variable,
} from '../../types';

import styled, { css } from 'styled-components';
import { Table } from '../../components/Table';

import { Column as ColumnType, RowRecord } from 'wprdc-components';
import { PieChart } from '../../components/PieChart';
import { Sentence } from '../../components/Sentence';
import BigValue from '../../components/BigValue';
import { BarChart } from '../../components/BarChart';
import { LineChart } from '../../components/LineChart';
import { MiniMap } from '../../components/MiniMap';

type DownloadedTable = Downloaded<TableViz, TableData>;
type Row = RowRecord;
type Column = ColumnType<Row>;

type VizGenerator<T extends DataVizBase, D extends DataVizData> = (
  dataViz: Downloaded<T, D>,
) => JSX.Element | null;

export function getSpecificDataViz(
  dataViz?: Downloaded<DataVizBase, DataVizData>,
) {
  if (!dataViz) {
    return null;
  }
  const generators: Record<DataVizResourceType, VizGenerator<any, any>> = {
    [DataVizResourceType.Sentence]: generateSentence,
    [DataVizResourceType.BigValue]: generateBigValue,
    [DataVizResourceType.MiniMap]: generateMiniMap,
    [DataVizResourceType.Table]: generateTable,
    [DataVizResourceType.PieChart]: generatePieChart,
    [DataVizResourceType.LineChart]: generateLineChart,
    [DataVizResourceType.LineChart]: generateLineChart,
    [DataVizResourceType.BarChart]: generateBarChart,
  };
  const generator = generators[dataViz.resourcetype];
  return generator(dataViz);
}

/*
 * Data Viz Generators
 */
const generateSentence: VizGenerator<SentenceViz, SentenceData> = dataViz => (
  <Sentence {...dataViz} />
);

const generateBigValue: VizGenerator<BigValueViz, BigValueData> = dataViz => {
  const items = dataViz.variables.map((variable, idx) => ({
    value: formatValue(variable, dataViz.data[idx].v),
    label: variable.name,
  }));

  return <BigValue data={items} />;
};

const generateMiniMap: VizGenerator<MiniMapViz, MiniMapData> = dataViz => (
  <MiniMap {...dataViz.data} />
);

const generateTable: VizGenerator<TableViz, TableData> = table => {
  // map data from API to format for Table
  const columns: Column[] = [
    {
      accessor: 'label',
      id: 'category',
    },
    ...table.timeAxis.timeParts.map(timePart => ({
      Header: timePart.name,
      accessor: timePart.slug,
    })),
  ];

  const data: Row[] = table.variables.map((variable, idx) => ({
    key: `${table.slug}/${variable.slug}`,
    label: variable.name,
    ...table.timeAxis.timeParts.reduce(rowValuesReducer(table, idx), {}),
    subRows: getPercentRows(table, variable, idx),
    expanded: true,
  }));

  return <Table columns={columns} data={data} />;
};

const generatePieChart: VizGenerator<PieChartViz, ChartData> = dataViz => {
  return (
    <PieChart
      data={dataViz.data}
      dataKey={dataViz.timeAxis.timeParts[0].slug}
    />
  );
};

const generateBarChart: VizGenerator<BarChartViz, ChartData> = dataViz => {
  return (
    <BarChart
      data={dataViz.data}
      dataKey={dataViz.timeAxis.timeParts[0].slug}
      barName={dataViz.timeAxis.timeParts[0].name}
    />
  );
};

const generateLineChart: VizGenerator<LineChartViz, ChartData> = dataViz => {
  return (
    <LineChart
      data={dataViz.data}
      dataKey={dataViz.timeAxis.timeParts[0].slug}
    />
  );
};

export function makeKey(dataVizID: DataVizID, region: RegionDescriptor) {
  return `${dataVizID.slug}@${region.regionType}/${region.regionID}`;
}

const MoEWrapper = styled.span`
  cursor: pointer;
  ${({ theme }) => css`
    color: #62a2ef;
  `}
`;

function MoE({ moe }: { moe: number }) {
  return (
    <MoEWrapper title={`Margin of Error: ${moe.toFixed(2)}`}>
      <sup>&#177;</sup>
    </MoEWrapper>
  );
}

function makeCellValue(d: DataVizDataPoint, v: Variable) {
  let displayValue = d.v;
  if (typeof d.v === 'number') {
    displayValue = d.v.toLocaleString(undefined, v.localeOptions || undefined);
  }
  return (
    <>
      {displayValue}
      {(d.m || d.m === 0) && <MoE moe={d.m} />}
    </>
  );
}

function getPercentValue(table: DownloadedTable, idx, denom, cur) {
  const percentValue: number = table.data[idx][cur.slug][denom.slug];
  return formatPercent(percentValue);
}

const rowValuesReducer = (table: DownloadedTable, idx) => (acc, cur) => ({
  ...acc,
  [cur.slug]: makeCellValue(table.data[idx][cur.slug], table.variables[idx]),
});

const percentRowValuesReducer = (table: DownloadedTable, idx, denom) => (
  acc,
  cur,
) => ({
  ...acc,
  [cur.slug]: getPercentValue(table, idx, denom, cur),
});

function getPercentRows(
  table: DownloadedTable,
  variable: Variable,
  idx: number,
) {
  return variable.denominators.map(denom => ({
    key: `${table.slug}/${variable.slug}/${denom.slug}`,
    label: denom.percentLabel,
    ...table.timeAxis.timeParts.reduce(
      percentRowValuesReducer(table, idx, denom),
      {},
    ),
    className: 'subrow',
  }));
}

function formatValue(
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

function formatPercent(value?: number): React.ReactNode {
  if (typeof value === 'number')
    return value.toLocaleString(undefined, {
      style: 'percent',
      minimumSignificantDigits: 1,
      maximumSignificantDigits: 3,
    });
  return 'N/A';
}
