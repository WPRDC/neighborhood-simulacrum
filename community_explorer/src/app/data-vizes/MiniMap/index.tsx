/**
 *
 * MiniMap
 *
 */
import React from 'react';
import { Legend, Map, SimpleLabelPopupContent } from 'wprdc-components';
import { MAPBOX_API_TOKEN } from '../../settings';
import { View } from '@adobe/react-spectrum';
import { ColorMode, MiniMapData, MiniMapViz, VizProps } from '../../types';

interface Props extends VizProps<MiniMapViz, MiniMapData> {
  colorScheme?: ColorMode;
}

export function MiniMap(props: Props) {
  const { dataViz, colorScheme, vizHeight, vizWidth } = props;
  const { sources, layers, mapOptions, legends } = dataViz.data;

  return (
    <View maxHeight="size-6000">
      <Map
        mapboxApiAccessToken={MAPBOX_API_TOKEN}
        width={vizWidth ? vizWidth + 13 : 0}
        height={vizHeight ? vizHeight + 13 : 0}
        defaultViewport={{ zoom: 8, longitude: -79.9925 }}
        hoverPopupContent={SimpleLabelPopupContent}
        hoverPopupContentProps={{
          getLabel: ({ primaryFeatureProps }) =>
            primaryFeatureProps && `${primaryFeatureProps.mapValue}`,
        }}
        legends={legends.map(legendProps => (
          <Legend {...legendProps} mode="mini" />
        ))}
        sources={sources}
        layers={layers}
        getCursor={() => 'crosshair'}
        minZoom={6}
        basemapStyle={colorScheme || ColorMode.Light}
        {...mapOptions}
      />
    </View>
  );
}
