/**
 *
 * Select
 *
 */
import React from 'react';

import ReactSelect, { NamedProps } from 'react-select';

import { Option } from './Option';
import { SingleValue } from './SingleValue';

interface Props<T = any> extends NamedProps<T> {
  options: T[];
}

const IndicatorSeparator = null;

export function Select(props: Props) {
  return (
    <ReactSelect
      {...props}
      components={{ Option, SingleValue, IndicatorSeparator }}
    />
  );
}
