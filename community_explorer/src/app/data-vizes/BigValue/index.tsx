/**
 *
 * BigValue
 *
 */
import React from 'react';

import { Text, View } from '@adobe/react-spectrum';
import { BigValueData, BigValueViz, VizProps } from '../../types';
import { formatValue } from '../../containers/DataViz/util';

interface Props extends VizProps<BigValueViz, BigValueData> {}

export function BigValue(props: Props) {
  const { dataViz } = props;
  const items = dataViz.variables.map((variable, idx) => ({
    value: formatValue(variable, dataViz.data[idx].v),
    label: variable.name,
  }));

  return (
    <View>
      {items &&
        items.map(({ value, label }) => (
          <View>
            <View padding="none">
              <Text
                UNSAFE_style={{
                  fontSize: '5rem',
                  fontWeight: 800,
                  padding: 0,
                  margin: 0,
                }}
              >
                {value}
              </Text>
            </View>
            <View>
              <Text>{label}</Text>
            </View>
          </View>
        ))}
    </View>
  );
}

export default BigValue;
