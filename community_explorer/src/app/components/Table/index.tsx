/**
 *
 * Table
 *
 */
import React, { ReactNode } from 'react';

import {
  Table as RSTable,
  TableHeader,
  TableBody,
  Column,
  Row,
  Cell,
} from '@react-spectrum/table';

interface Props {}

interface Props {
  columns: ColumnData[];
  rows: RowData[];
}

interface ColumnData {
  label: ReactNode;
  key?: string;
}

interface RowData {
  key?: string;
  cells: CellData[];
}

type CellData = {
  key?: string;
  value: ReactNode;
};

export function Table(props: Props) {
  const { columns, rows } = props;

  return (
    <RSTable>
      <TableHeader>
        {columns.map(column => (
          <Column key={column.key}>{column.label}</Column>
        ))}
      </TableHeader>
      <TableBody>
        {rows.map(row => (
          <Row key={row.key}>
            {row.cells.map(cell => (
              <Cell key={cell.key}>{cell.value}</Cell>
            ))}
          </Row>
        ))}
      </TableBody>
    </RSTable>
  );
}
