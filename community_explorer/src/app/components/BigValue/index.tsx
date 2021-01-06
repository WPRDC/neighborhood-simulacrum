/**
 *
 * BigValue
 *
 */
import React from 'react';
import { BigValueData } from '../../types';

import { Text } from '@adobe/react-spectrum';
import { View } from '@react-spectrum/view';

interface Props {
  data: BigValueData;
  note?: string;
}

export function BigValue(props: Props) {
  console.log(props);
  return (
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
          ${props.data.v}
        </Text>
      </View>
      <View>
        <Text>{props.note}</Text>
      </View>
    </View>
  );
}

export default BigValue;
