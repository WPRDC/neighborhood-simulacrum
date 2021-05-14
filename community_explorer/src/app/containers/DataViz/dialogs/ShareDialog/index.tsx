/**
 *
 * ShareDialog
 *
 */
import React from 'react';
import { DataVizBase, Downloaded } from '../../../../types';
import {
  Content,
  Dialog,
  Divider,
  Heading,
  Link,
  Text,
} from '@adobe/react-spectrum';

interface Props {
  onClose: () => void;
  dataViz: Downloaded<DataVizBase>;
}

export function ShareDialog(props: Props) {
  const { onClose, dataViz } = props;
  return (
    <Dialog isDismissable onDismiss={onClose}>
      <Heading>Share this Data</Heading>
      <Divider />
      <Content>
        <Text>
          <p>Sharing options coming soon...</p>
          <p>
            Until then, you can share this link for the indicator:{' '}
            <Link>
              <a href={window.location.href}>{window.location.href}</a>
            </Link>
          </p>
        </Text>
      </Content>
    </Dialog>
  );
}
