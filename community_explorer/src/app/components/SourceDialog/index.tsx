/**
 *
 * SourceDialog
 *
 */
import React from 'react';
import styled from 'styled-components/macro';
import {
  Content,
  Dialog,
  Divider,
  Heading,
  Link,
  Text,
} from '@adobe/react-spectrum';
import { SourceBase } from '../../types';

interface Props {
  onClose: () => void;
  source: SourceBase;
}

export function SourceDialog(props: Props) {
  const { onClose, source } = props;
  return (
    <Dialog isDismissable onDismiss={onClose}>
      <Heading>{source.name}</Heading>
      <Divider />
      <Content>
        <Text>
          <p>{source.description}</p>
        </Text>
        <Link>
          <a href={source.infoLink} target="_blank" rel="noreferrer noopener">
            {source.infoLink}
          </a>
        </Link>
      </Content>
    </Dialog>
  );
}
