/**
 *
 * NavMenu
 *
 */
import React, { Key } from 'react';
import { GeogTypeDescriptor } from '../../containers/Explorer/types';
import { Heading, Item, Picker, Text, View } from '@adobe/react-spectrum';
import { GeogDescriptor, GeogIdentifier, GeographyType } from '../../types';

interface Props {
  geoLayers?: GeogTypeDescriptor[];
  geoLayersIsLoading: boolean;
  selectedGeoLayer?: GeogTypeDescriptor;
  selectedGeog?: GeogIdentifier;
  onLayerSelect: (geoLayer: GeogTypeDescriptor) => void;
  onGeogSelect: (geog: GeogIdentifier) => void;
  geogsListsRecord: Record<GeographyType, GeogDescriptor[]>;
  geogsListsAreLoadingRecord: Record<GeographyType, boolean>;
}

export function NavMenu(props: Props) {
  const {
    geoLayers,
    geoLayersIsLoading,
    selectedGeoLayer,
    selectedGeog,
    onLayerSelect,
    onGeogSelect,
    geogsListsRecord,
    // geogsListsAreLoadingRecord,
  } = props;

  // console.debug(props);

  function handleAreaSelect(selectedSlug: Key) {
    if (geoLayers) {
      const selectedLayer = geoLayers.filter(
        ({ id }) => id === selectedSlug,
      )[0];
      onLayerSelect(selectedLayer);
    }
  }

  function handleGeogSelect(selectedKey: Key) {
    const [geogType, geogID] = splitKey(selectedKey as string);
    onGeogSelect({ geogType, geogID });
  }

  const [selectedGeoLayerID, selectedGeoLayerName] = selectedGeoLayer
    ? [selectedGeoLayer.id, selectedGeoLayer.name]
    : [undefined, undefined];
  const geogs = selectedGeoLayerID ? geogsListsRecord[selectedGeoLayerID] : [];
  const selectedGeogKey = selectedGeog ? makeGeogKey(selectedGeog) : undefined;

  // console.debug({ geogs, selectedGeogKey });

  return (
    <View paddingX="size-200">
      <Heading level={2}>Select an area to explore</Heading>
      <Text>
        Use the dropdown and the map to find the place you're interested in.
      </Text>
      <View paddingTop="size-200">
        {!!geoLayers && !!selectedGeoLayerID && !!geogs && (
          <>
            <Picker<GeogTypeDescriptor>
              label="Type of Area"
              items={geoLayers}
              selectedKey={selectedGeoLayerID}
              onSelectionChange={handleAreaSelect}
              width="100%"
            >
              {item => <Item>{item.name}</Item>}
            </Picker>
            <Picker<GeogDescriptor>
              label={selectedGeoLayerName}
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
          </>
        )}
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
