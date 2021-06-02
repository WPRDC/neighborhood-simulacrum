/*
 *
 * utils.ts
 *
 * Utility functions
 *
 */

import { RowRecord } from './types';

export const addReactSelectKeys = (
  option: {} | {}[] = {},
  keyMapping: Record<'label' | 'value', string> = {
    label: 'name',
    value: 'slug',
  },
) => {
  const options = Array.isArray(option) ? option : [option];
  return options.map(opt =>
    Object.assign(
      {
        label: keyMapping.label ? option[keyMapping.label] : undefined,
        value: keyMapping.value ? option[keyMapping.value] : undefined,
      },
      opt,
    ),
  );
};

export function dumpCSV(data: RowRecord[]): string {
  return data.reduce((csv, row, i) => {
    if (i === 0) {
      return `${_csvHeader(row)}\n${_csvRow(row)}`;
    }
    return `${csv}\n${_csvRow(row)}`;
  }, '');
}

function _csvHeader(row: RowRecord): string {
  return Object.keys(row)
    .map(k => `"${k}"`)
    .join(',');
}

function _csvRow(row: RowRecord): string {
  return Object.values(row)
    .map(v => (typeof v === 'string' ? `"${v}` : v))
    .join(',');
}
