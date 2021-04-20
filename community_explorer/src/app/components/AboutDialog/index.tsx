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
      <Heading>About this thing</Heading>
      <Image
        slot="hero"
        src={isometricCityJPG}
        alt="Isometric City Illustration"
        objectFit="cover"
        top={60}
      ></Image>
      <Divider />
      <Content>
        <Text>
          <p>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus
            sem libero, tincidunt non sodales eu, cursus eget orci. Duis lacus
            nibh, posuere eget bibendum id, faucibus et massa. Maecenas sodales
            nisi non augue commodo, eu sodales ligula blandit. Sed non rhoncus
            lacus, id rhoncus quam. Praesent sed orci non enim vestibulum
            congue. Duis vel mauris eu lectus auctor faucibus. Duis accumsan
            hendrerit feugiat. In a augue elementum, venenatis justo et, congue
            purus. Aliquam eget arcu ac lectus feugiat sagittis. Pellentesque
            vel eros tincidunt, rhoncus sapien vel, dapibus tortor. Integer
            cursus neque purus, sed eleifend leo maximus id. Nunc congue, urna
            sit amet placerat pulvinar, orci odio rutrum turpis, vel facilisis
            magna est aliquet purus.{' '}
          </p>
          <ul>
            <li>Something</li>
            <li>Another thing</li>
            <li>I guess another thing if thats what folks want.</li>
          </ul>
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
