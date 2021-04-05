/**
 *
 * NavMenu
 *
 */
import React, { Key } from 'react';
import { GeoLayer } from '../../containers/Explorer/types';
import { View, Item, Heading, Text, Picker } from '@adobe/react-spectrum';
import { GEO_CATEGORIES } from '../../settings';

interface Props {
  selectedGeoLayer: GeoLayer;
  handleLayerSelect: (geoLayer: GeoLayer) => void;
}

export function NavMenu(props: Props) {
  const { selectedGeoLayer, handleLayerSelect } = props;

  function handleAreaSelect(selectedSlug: Key) {
    console.log(selectedSlug);
    let selectedLayer = GEO_CATEGORIES.filter(
      ({ id }) => id === selectedSlug,
    )[0];
    handleLayerSelect(selectedLayer);
  }

  return (
    <View paddingX="size-100">
      <Heading level={2}>Select an area to explore</Heading>
      <Text>
        Use the dropdown and the map to find the place you're interested in.
      </Text>
      <View paddingTop="size-200">
        <Picker<GeoLayer>
          label="Type of Area"
          items={GEO_CATEGORIES}
          selectedKey={selectedGeoLayer.id}
          onSelectionChange={handleAreaSelect}
          width="100%"
        >
          {item => <Item>{item.name}</Item>}
        </Picker>
      </View>
    </View>
  );
}
