/**
 *
 * BigValue
 *
 */
import React from 'react';

import { Text, View } from '@adobe/react-spectrum';
import { BigValueViz, TabularData, VizProps } from '../../types';
import styled from 'styled-components/macro';

interface Props extends VizProps<BigValueViz, TabularData> {}

export function BigValue(props: Props) {
  const { dataViz } = props;
  const { data, error } = dataViz;

  if (!data || !data[0]) return <View />;
  if (error.level) {
    return (
      <View>
        <Text>{error.message}</Text>
      </View>
    );
  }

  const { variable, value, percent, denom } = data[0];
  const primaryVariable = dataViz.variables.find(v => v.slug === variable);

  const denomVariable =
    primaryVariable && primaryVariable.denominators
      ? primaryVariable.denominators[0]
      : undefined;

  const displayValue =
    typeof value === 'number'
      ? value.toLocaleString(
          'en-US',
          primaryVariable ? primaryVariable.localeOptions : undefined,
        )
      : undefined;

  const displayPercent =
    typeof percent === 'number' ? (
      <span style={{ fontSize: '3rem' }}>
        {' '}
        ({percent.toLocaleString('en-US', { style: 'percent' })})
      </span>
    ) : undefined;

  const displayDenom =
    typeof denom === 'number' ? (
      <span style={{ fontSize: '3rem' }}>
        {' / '}
        {denom.toLocaleString(
          'en-US',
          denomVariable ? denomVariable.localeOptions : undefined,
        )}
      </span>
    ) : undefined;
  return (
    <View>
      <Text>
        <BigValueText
          style={{
            fontSize: '5rem',
            fontWeight: 800,
            padding: 0,
            margin: 0,
          }}
        >
          {displayValue}
          {displayDenom}
          {displayPercent}
        </BigValueText>
        <NoteText>{dataViz.name}</NoteText>
      </Text>
    </View>
  );
}

const BigValueText = styled.p`
  font-size: 5rem;
  line-height: 5rem;
  font-weight: 800;
  padding: 0;
  margin: 0;
`;

const NoteText = styled.p`
  font-size: 1.4rem;
  color: var(--spectrum-global-color-gray-700);
  line-height: 2rem;
  font-weight: 500;
  padding: 0;
  margin: 0;
`;

export default BigValue;
