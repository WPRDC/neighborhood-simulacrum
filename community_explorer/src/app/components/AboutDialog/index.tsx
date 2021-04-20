/**
 *
 * AboutDialog
 *
 */
import {
  Text,
  Content,
  Dialog,
  Divider,
  Heading,
  Image,
  Link,
} from '@adobe/react-spectrum';
import React from 'react';

import isometricCityJPG from '../../images/iso_city2.jpg';

interface Props {
  onClose: () => void;
}

const imgAttribution = (
  <a href="https://www.freepik.com/vectors/background">
    Background vector created by macrovector
  </a>
);

export function AboutDialog(props: Props) {
  const { onClose } = props;
  return (
    <Dialog isDismissable onDismiss={onClose}>
      <Heading>What is this?</Heading>
      <Divider />
      <Content>
        <Text>
          <p>
            The Children's Health Data Explorer is designed to provide residents
            of Allegheny County with a way to explore data in their communities
            and help make sense of the information.{' '}
          </p>
          <p>
            The Children’s Health Data Explorer presents community data and
            indicators in a series of tables, charts and maps. Data comes from
            local, state, and federal government sources. Data are available by
            different geographies, from county and municipal levels down to
            neighborhood and census tract and block groupings. Not all
            information is available along all geographies, but much is.
          </p>
        </Text>
        <Link
          variant="secondary"
          UNSAFE_style={{ fontSize: '10px', fontStyle: 'italic' }}
        >
          {imgAttribution}
        </Link>
      </Content>
    </Dialog>
  );
}
