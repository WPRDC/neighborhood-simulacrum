/**
 *
 * MissingVizMessage
 *
 */
import {
  Content,
  Flex,
  Heading,
  IllustratedMessage,
} from '@adobe/react-spectrum';
import NotFound from '@spectrum-icons/illustrations/NotFound';
import React from 'react';

interface Props {
  error?: string;
}

export function MissingVizMessage(props: Props) {
  const { error } = props;
  return (
    <Flex justifyContent="center" alignContent="center">
      <IllustratedMessage width="size-2400">
        <NotFound />
        <Heading>No results</Heading>
        <Content>{error || 'Error generating data viz.'}</Content>
      </IllustratedMessage>
    </Flex>
  );
}
