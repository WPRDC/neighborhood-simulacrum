/**
 *
 * LoadingMessage
 *
 */
import React from 'react';
import { Flex, ProgressCircle, View, Text } from '@adobe/react-spectrum';

interface Props {}

export function LoadingMessage(props: Props) {
  return (
    <Flex
      height="100%"
      width="100%"
      justifyContent="center"
      alignItems="center"
    >
      <View>
        <View>
          <ProgressCircle
            size="L"
            isIndeterminate
            aria-labelledby="loadingText"
          />
        </View>
        <View>
          <Text id="loadingText">Loading viz...</Text>
        </View>
      </View>
    </Flex>
  );
}
