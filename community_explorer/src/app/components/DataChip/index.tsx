/**
 *
 * DataChip
 *
 */
import React, { memo } from 'react';
import styled from 'styled-components/macro';
import { Datum } from '../../types/common';
import { View, Text, Flex } from '@adobe/react-spectrum';

interface Props {
  title: string;
  icon: React.ReactNode;
  value: Datum;
}

export const DataChip = memo((props: Props) => {
  const { title, icon, value } = props;
  let displayValue = value;
  if (typeof value === 'number') displayValue = value.toLocaleString();

  return (
    <View
      borderRadius="small"
      borderWidth="thin"
      margin="size-100"
      width="auto"
    >
      <Flex>
        <View backgroundColor="gray-200" paddingX="size-100" paddingY="size-25">
          <Flex>
            <View marginBottom="size-10">{icon}</View>
            <Text marginStart="size-25">{title}</Text>
          </Flex>
        </View>
        <View
          backgroundColor="gray-50"
          paddingY="size-25"
          paddingX="size-100"
          minWidth="size-350"
        >
          <Text>{displayValue}</Text>
        </View>
      </Flex>
    </View>
  );
});

const Div = styled.div``;
