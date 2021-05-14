/*
 *
 * utils.ts
 *
 * Utility functions
 *
 */

import {GeographyType, RowRecord} from './types';
import { GEOG_TYPES } from './settings';
import { GeogTypeDescriptor } from './containers/Explorer/types';

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

type DataRow = Record<string, string | number | boolean>;

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

export function getDescriptorForGeogType(
  targetGeogType: string,
): GeogTypeDescriptor | undefined {
  if ((Object as any).values(GeographyType).includes(targetGeogType)) {
    const results = GEOG_TYPES.filter(
      ({ id }) => id === (targetGeogType as GeographyType),
    );
    if (!!results) {
      return results[0];
    }
  }
  return undefined;
}
