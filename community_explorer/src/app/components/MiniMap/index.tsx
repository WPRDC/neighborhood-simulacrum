/**
 *
 * MiniMap
 *
 */
import React from 'react';
import {
  LayerOptions,
  Legend,
  LegendProps,
  Map,
  MapProps,
  SimpleLabelPopupContent,
} from 'wprdc-components';
import { SourceProps } from 'react-map-gl';
import { MAPBOX_API_TOKEN } from '../../settings';
import { View } from '@react-spectrum/view';

interface Props {
  sources: SourceProps[];
  layers: LayerOptions[];
  mapOptions: Partial<MapProps>;
  legends: LegendProps[];
}

export function MiniMap(props: Props) {
  const { sources, layers, mapOptions, legends } = props;

  return (
    <View borderWidth="thin" height="size-3400">
      <Map
        mapboxApiAccessToken={MAPBOX_API_TOKEN}
        width="100%"
        height="100%"
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
        {...mapOptions}
      />
    </View>
  );
}
