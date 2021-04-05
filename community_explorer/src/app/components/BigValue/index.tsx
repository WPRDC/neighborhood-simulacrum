/**
 *
 * BigValue
 *
 */
import React from 'react';

import { Text, View } from '@adobe/react-spectrum';

interface Props {
  data: { value: React.ReactNode; label: React.ReactNode }[];
  note?: string;
}

export function BigValue(props: Props) {
  const { data } = props;

  return (
    <View>
      {data &&
        data.map(({ value, label }) => (
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
