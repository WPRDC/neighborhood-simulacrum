import React from 'react';

import {
  DataVizID,
  DataVizDataPoint,
  DataVizResourceType,
  RegionDescriptor,
  TableData,
  DataVisualization,
  TableViz,
  Downloaded,
  Variable,
  PieChartViz,
  ChartData,
  SentenceViz,
  SentenceData,
  BigValueViz,
  BigValueData,
} from '../../types';

import styled, { css } from 'styled-components';
import { Table } from '../../components/Table';

import { Column as ColumnType, RowRecord } from 'wprdc-components';
import { PieChart } from '../../components/PieChart';
import { Sentence } from '../../components/Sentence';
import BigValue from '../../components/BigValue';

type DownloadedTable = Downloaded<TableViz, TableData>;
type Row = RowRecord;
type Column = ColumnType<Row>;

// fixme:  too much important work is being done by this random function and its awkward to read
export function getSpecificDataViz(dataViz?: DataVisualization) {
  if (!dataViz) {
    return null;
  }
  switch (dataViz.resourcetype) {
    case DataVizResourceType.Table:
      const { columns, data: tableData } = generateTableProps(
        dataViz as Downloaded<TableViz, TableData>,
      );
      return <Table columns={columns} data={tableData} />;

    case DataVizResourceType.PieChart:
      let { data: chartData, dataKey } = generatePieChartProps(
        dataViz as Downloaded<PieChartViz, ChartData>,
      );
      return <PieChart data={chartData} dataKey={dataKey} />;

    case DataVizResourceType.Sentence:
      const { text, sentenceData } = generateSentenceProps(
        dataViz as Downloaded<SentenceViz, SentenceData>,
      );
      return <Sentence text={text} data={sentenceData} />;

    case DataVizResourceType.BigValue:
      const { note, data: bigValueData } = dataViz as Downloaded<
        BigValueViz,
        BigValueData
      >;
      return <BigValue data={bigValueData} note={note} />;

    default:
      return null;
  }
}

function generateSentenceProps(dataViz: Downloaded<SentenceViz, SentenceData>) {
  const { text, data } = dataViz;
  return {
    text,
    sentenceData: data,
  };
}

function generateTableProps(
  table: DownloadedTable,
): { columns: Column[]; data: Row[] } {
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

  return { columns, data };
}

function generatePieChartProps(response: Downloaded<PieChartViz, ChartData>) {
  return { data: response.data, dataKey: response.timeAxis.timeParts[0].slug };
}

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

function makeCellValue(d: DataVizDataPoint) {
  let displayValue = d.v;
  if (typeof d.v === 'number') {
    displayValue = d.v.toLocaleString();
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
  return percentValue.toLocaleString(undefined, {
    style: 'percent',
    minimumSignificantDigits: 1,
    maximumSignificantDigits: 3,
  });
}

const rowValuesReducer = (table: DownloadedTable, idx) => (acc, cur) => ({
  ...acc,
  [cur.slug]: makeCellValue(table.data[idx][cur.slug]),
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
