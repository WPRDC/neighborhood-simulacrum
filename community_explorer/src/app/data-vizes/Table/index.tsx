/**
 *
 * Table
 *
 */
import React from 'react';

import { Column, RowRecord, Table as WTable } from 'wprdc-components';
import {
  DataVizDataPoint,
  Downloaded,
  TableData,
  TableViz,
  Variable,
  VizProps,
} from '../../types';
import styled from 'styled-components';
import { formatCategory, formatPercent } from '../../containers/DataViz/util';
import { View } from '@adobe/react-spectrum';

interface Props extends VizProps<TableViz, TableData> {}

export function Table(props: Props) {
  const { dataViz } = props;
  const { timeAxis, variables } = dataViz;
  // map data from API to format for Table
  const columns: Column<RowRecord>[] = [
    {
      accessor: 'label',
      id: 'category',
    },
    ...timeAxis.timeParts.map(timePart => ({
      Header: timePart.name,
      accessor: timePart.slug,
    })),
  ];

  const data: RowRecord[] = variables.map((variable, idx) => ({
    key: `${dataViz.slug}/${variable.slug}`,
    label: formatCategory(variable),
    ...timeAxis.timeParts.reduce(makeRowValuesReducer(dataViz, idx), {}),
    subRows: getPercentRows(dataViz, variable, idx),
    expanded: true,
  }));

  return (
    <View padding="size-100">
      <WTable columns={columns} data={data} />
    </View>
  );
}

const makeRowValuesReducer = (table: Downloaded<TableViz, TableData>, idx) => (
  acc,
  cur,
) => ({
  ...acc,
  [cur.slug]: makeCellValue(table.data[idx][cur.slug], table.variables[idx]),
});

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

const MoEWrapper = styled.span`
  cursor: pointer;
  color: #62a2ef;
`;

function MoE({ moe }: { moe: number }) {
  return (
    <MoEWrapper title={`Margin of Error: ${moe.toFixed(2)}`}>
      <sup>&#177;</sup>
    </MoEWrapper>
  );
}

function getPercentValue(
  table: Downloaded<TableViz, TableData>,
  idx,
  denom,
  cur,
) {
  const percentValue: number = table.data[idx][cur.slug][denom.slug];
  return formatPercent(percentValue);
}

const percentRowValuesReducer = (
  table: Downloaded<TableViz, TableData>,
  idx,
  denom,
) => (acc, cur) => ({
  ...acc,
  [cur.slug]: getPercentValue(table, idx, denom, cur),
});

function getPercentRows(
  table: Downloaded<TableViz, TableData>,
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
