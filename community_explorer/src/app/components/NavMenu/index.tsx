/**
 *
 * NavMenu
 *
 */
import React, { Key } from 'react';
import { GeogTypeDescriptor } from '../../containers/Explorer/types';
import { Heading, Item, Picker, Text, View } from '@adobe/react-spectrum';
import { GEOG_TYPES } from '../../settings';
import { GeogDescriptor, GeogIdentifier, GeographyType } from '../../types';

interface Props {
  selectedGeoLayer: GeogTypeDescriptor;
  selectedGeog: GeogIdentifier;
  onLayerSelect: (geoLayer: GeogTypeDescriptor) => void;
  onGeogSelect: (geog: GeogIdentifier) => void;
  geogsListsRecord: Record<GeographyType, GeogDescriptor[]>;
  geogsListsAreLoadingRecord: Record<GeographyType, boolean>;
}

export function NavMenu(props: Props) {
  const {
    selectedGeoLayer,
    selectedGeog,
    onLayerSelect,
    onGeogSelect,
    geogsListsRecord,
    // geogsListsAreLoadingRecord,
  } = props;

  function handleAreaSelect(selectedSlug: Key) {
    const selectedLayer = GEOG_TYPES.filter(({ id }) => id === selectedSlug)[0];
    onLayerSelect(selectedLayer);
  }

  function handleGeogSelect(selectedKey: Key) {
    const [geogType, geogID] = splitKey(selectedKey as string);
    onGeogSelect({ geogType, geogID });
  }

  // const geogsLoading = geogsListsAreLoadingRecord[selectedGeoLayer.id];
  const geogs = geogsListsRecord[selectedGeoLayer.id] || [];
  const selectedGeogKey = makeGeogKey(selectedGeog);
  // handle selection of said geog from picker
  // whole app needs to get state of selected geog from same place
  // this and the navmap must update the selected geog through the same action

  return (
    <View paddingX="size-200">
      <Heading level={2}>Select an area to explore</Heading>
      <Text>
        Use the dropdown and the map to find the place you're interested in.
      </Text>
      <View paddingTop="size-200">
        <Picker<GeogTypeDescriptor>
          label="Type of Area"
          items={GEOG_TYPES}
          selectedKey={selectedGeoLayer.id}
          onSelectionChange={handleAreaSelect}
          width="100%"
        >
          {item => <Item>{item.name}</Item>}
        </Picker>
        <Picker<GeogDescriptor>
          label={selectedGeoLayer.name}
          items={geogs}
          selectedKey={selectedGeogKey}
          onSelectionChange={handleGeogSelect}
          width="100%"
        >
          {item => (
            <Item key={makeGeogKey(item)}>
              <Text>{item.title}</Text>
            </Item>
          )}
        </Picker>
      </View>
    </View>
  );
}

function makeGeogKey(geog: GeogIdentifier) {
  return `${geog.geogType}/${geog.geogID}`;
}

function splitKey(key: string) {
  return key.split('/');
}
