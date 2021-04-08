/**
 *
 * Table
 *
 */
import React from 'react';

import { Column, RowRecord, Table as WTable } from 'wprdc-components';

interface Props {
  columns: Column<RowRecord>[];
  data: RowRecord[];
}

export function Table(props: Props) {
  return <WTable {...props} />;
}
