/**
 *
 * ActionDialog
 *
 */
import {
  Content,
  Dialog,
  Divider,
  Heading,
  Link,
  Text,
} from '@adobe/react-spectrum';
import React from 'react';
import { DataVizID } from '../../types';

interface Props {
  onClose: () => void;
  dataVizID: DataVizID;
}

export function UserReportDialog(props: Props) {
  const { onClose, dataVizID } = props;
  const emailLink = `mailto:wprdc@pitt.edu?subject=Profiles data viz issue - ${dataVizID.name}`;
  return (
    <Dialog isDismissable onDismiss={onClose}>
      <Heading>Report a Data Error</Heading>
      <Divider />
      <Content>
        <Text>
          <p>
            Is there a problem with the his data visualization? Please{' '}
            <Link>
              <a href={emailLink}>let us know</a>
            </Link>
            .
          </p>
        </Text>
      </Content>
    </Dialog>
  );
}
