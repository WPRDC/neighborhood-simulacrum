import React from 'react';
import { components, SingleValueProps } from 'react-select';
import { Text } from '@adobe/react-spectrum';

interface Props extends SingleValueProps<any> {}

export function SingleValue(props: Props) {
  return (
    <components.SingleValue {...props}>
      <Text UNSAFE_style={{ fontWeight: 'bold' }}>{props.data.name}</Text>
    </components.SingleValue>
  );
}

SingleValue.propTypes = components.SingleValue.propTypes;
