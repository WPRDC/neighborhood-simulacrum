/**
 *
 * NavMenu
 *
 */
import React from 'react';
import { GeoLayer } from '../../containers/Explorer/types';
import { View } from '@react-spectrum/view';
import { Heading, Text } from '@react-spectrum/text';
import { GEO_CATEGORIES } from '../../settings';
import { Select } from '../Select';
import { addReactSelectKeys } from '../../util';

interface Props {
  selectedGeoLayer: GeoLayer;
  handleLayerSelect: (geoLayer: GeoLayer) => void;
}

export function NavMenu(props: Props) {
  const { selectedGeoLayer, handleLayerSelect } = props;

  const options = addReactSelectKeys(GEO_CATEGORIES);
  const defaultValue = addReactSelectKeys(selectedGeoLayer)[0];

  return (
    <View paddingX="size-100">
      <Heading level={2}>Select a region to explore</Heading>
      <Text>
        This flight has only been beamed by a colorful admiral. Carnivorous,
        boldly ships accelerative open a strange, small creature. moon, energy,
        and hypnosis.
      </Text>
      <View paddingTop="size-200">
        <Text>Area category</Text>
        <Select
          isSearchable={false}
          isClearable={false}
          options={options}
          defaultValue={defaultValue}
          onChange={handleLayerSelect}
        />
      </View>
    </View>
  );
}
