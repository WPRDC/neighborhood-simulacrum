/**
 *
 * MiniMap
 *
 */
import React from 'react';
import { Legend, Map, SimpleLabelPopupContent } from 'wprdc-components';
import { MAPBOX_API_TOKEN } from '../../settings';
import { View } from '@adobe/react-spectrum';
import { ColorMode, MiniMapOptions, MiniMapViz, VizProps } from '../../types';

interface Props extends VizProps<MiniMapViz, MiniMapOptions> {
  colorScheme?: ColorMode;
}

export function MiniMap(props: Props) {
  const { dataViz, colorScheme, vizHeight, vizWidth } = props;
  if (!dataViz.options) return <div />;
  const {
    sources,
    layers,
    mapOptions,
    legends,
    localeOptions,
  } = dataViz.options;

  function getLabel({ primaryFeatureProps }) {
    if (primaryFeatureProps) {
      const { title, mapValue } = primaryFeatureProps;
      let displayValue = mapValue;

      if (typeof mapValue === 'number') {
        displayValue = mapValue.toLocaleString('en-US', localeOptions);
      }

      return (
        <div>
          {title}: <strong>{displayValue}</strong>
        </div>
      );
    }
  }

  return (
    <View maxHeight="size-6000">
      <Map
        mapboxApiAccessToken={MAPBOX_API_TOKEN}
        width={vizWidth ? vizWidth + 13 : 0}
        height={vizHeight ? vizHeight + 13 : 0}
        defaultViewport={{ zoom: 8, longitude: -79.9925 }}
        hoverPopupContent={SimpleLabelPopupContent}
        hoverPopupContentProps={{
          getLabel: getLabel,
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
