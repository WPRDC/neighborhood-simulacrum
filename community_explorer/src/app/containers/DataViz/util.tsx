import React from 'react';

import {
  DataVizID,
  DataVizDataPoint,
  DataVizResourceType,
  RegionID,
  TableData,
  DataVisualization,
  TableViz,
  Downloaded,
} from '../../types';

import { Column, Row } from 'wprdc-components';
import styled, { css } from 'styled-components';
import { Table } from '../../components/Table';

export function makeKey(dataVizID: DataVizID, region: RegionID) {
  return `${dataVizID.slug}@${region.regionType}/${region.geoid}`;
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

function generateCellValue(d: DataVizDataPoint) {
  return (
    <>
      {d.v}
      {(d.m || d.m === 0) && <MoE moe={d.m} />}
    </>
  );
}

function generateTableProps(
  table: Downloaded<TableViz, TableData>,
): { columns: Column[]; rows: Row[] } {
  // for the category column
  const catHeader = { label: '', key: `${table.slug}/category` };

  const columns: Column[] = [
    catHeader,
    ...table.timeAxis.timeParts.map(timePart => ({
      label: timePart.name,
      key: `${table.slug}/${timePart.slug}`,
    })),
  ];

  const rows: Row[] = table.variables.map((variable, i) => ({
    key: `${table.slug}/${variable.slug}`,
    cells: [
      {
        key: `${table.slug}/${variable.slug}/label`,
        value: variable.name,
      },
      ...table.timeAxis.timeParts.map(timePart => ({
        key: `${table.slug}/${variable.slug}@${timePart.slug}`,
        value: generateCellValue(table.data[i][timePart.slug]),
      })),
    ],
  }));

  return { columns, rows };
}

export function getSpecificDataViz(dataViz?: DataVisualization) {
  if (!dataViz) {
    return null;
  }
  switch (dataViz.resourcetype) {
    case DataVizResourceType.Table:
      // get columns and rows from the data
      const { columns, rows } = generateTableProps(
        dataViz as Downloaded<TableViz, TableData>,
      );
      return <Table columns={columns} rows={rows} />;
    case DataVizResourceType.PieChart:
      // todo: implement chart stuff
      return null;
    case DataVizResourceType.MiniMap:
      // todo: implement map vizes
      return null;
    default:
      return null;
  }
}
