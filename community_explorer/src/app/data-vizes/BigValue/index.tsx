/**
 *
 * BigValue
 *
 */
import React from 'react';

import { Text, View } from '@adobe/react-spectrum';
import { BigValueData, BigValueViz, VizProps } from '../../types';
import styled from 'styled-components/macro';

interface Props extends VizProps<BigValueViz, BigValueData> {}

export function BigValue(props: Props) {
  const { dataViz } = props;
  const { v, p, d, localeOptions, note } = dataViz.data;
  const value = v.toLocaleString('en-US', localeOptions.v);
  const percent =
    typeof p === 'number' ? (
      <span style={{ fontSize: '3rem' }}>
        {' '}
        ({p.toLocaleString('en-US', localeOptions.p)})
      </span>
    ) : undefined;
  const denom =
    typeof d === 'number' ? (
      <span style={{ fontSize: '3rem' }}>
        {' / '}
        {d.toLocaleString('en-US', localeOptions.d)}
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
          {value}
          {denom}
          {percent}
        </BigValueText>
        <NoteText>{note || dataViz.name}</NoteText>
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
