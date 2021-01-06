/**
 *
 * Table
 *
 */
import React from 'react';

import { Table as WTable, Column, RowRecord } from 'wprdc-components';

interface Props {
  columns: Column<RowRecord>[];
  data: RowRecord[];
}

export function Table(props: Props) {
  return <WTable {...props} />;
}
