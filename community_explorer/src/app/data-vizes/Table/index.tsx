/**
 *
 * Table
 *
 */
import React from 'react';

import { Column, RowRecord, Table as WTable } from 'wprdc-components';
import {
  Downloaded,
  TableData,
  TableDatum,
  TableViz,
  TimePart,
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
  try {
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
  catch(e){
    console.error(e)
    return <div/>
  }
}

const makeRowValuesReducer = (table: Downloaded<TableViz, TableData>, idx) => (
  acc,
  cur,
) => ({
  ...acc,
  [cur.slug]: makeCellValue(table.data[idx][cur.slug], table.variables[idx]),
});

function makeCellValue(d: TableDatum, v: Variable) {
  let displayValue = d.value;
  if (typeof d.value === 'number') {
    displayValue = d.value.toLocaleString(
      undefined,
      v.localeOptions || undefined,
    );
  }
  return (
    <>
      {displayValue}
      {typeof d.moe === 'number' && <MoE moe={d.moe} />}
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

const percentRowValuesReducer = (
  table: Downloaded<TableViz, TableData>,
  idx: number,
  denom: Variable,
) => (acc, cur) => ({
  ...acc,
  [cur.slug]: getPercentValue(table, idx, denom, cur),
});

function getPercentValue(
  table: Downloaded<TableViz, TableData>,
  idx: number,
  denom: Variable,
  cur: TimePart,
) {
  const percentValue = table.data[idx][cur.slug].percent;
  return formatPercent(percentValue);
}
