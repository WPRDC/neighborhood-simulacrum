/**
 *
 * ApiDialog
 *
 */
import React from 'react';
import { DataVizBase, Downloaded } from '../../../../types';
import { Content, Dialog, Divider, Heading, Link } from '@adobe/react-spectrum';

interface Props {
  onClose: () => void;
  dataViz: Downloaded<DataVizBase>;
}

export function ApiDialog(props: Props) {
  const { onClose, dataViz } = props;
  const { id, geog } = dataViz;
  const host = 'https://api.profiles.wprdc.org';
  const apiUrl = `${host}/data-viz/${id}/?geogType=${geog.geogType}&geogID=${geog.geogID}`;

  return (
    <Dialog isDismissable onDismiss={onClose}>
      <Heading>Use this data in your app</Heading>
      <Divider />
      <Content>
        <Link>
          <a href={apiUrl}>{apiUrl}</a>
        </Link>
      </Content>
    </Dialog>
  );
}
