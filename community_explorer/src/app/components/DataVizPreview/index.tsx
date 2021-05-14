/**
 *
 * DataVizPreview
 *
 */
import React, { memo } from 'react';
import { View } from '@adobe/react-spectrum';
import Measure from 'react-measure';
import { VizWrapperProps } from '../../types';
import { MissingVizMessage } from '../MissingVizMessage';

interface Props extends VizWrapperProps {}

export const DataVizPreview = memo((props: Props) => {
  const { dataViz, geogIdentifier, colorScheme, CurrentViz, error } = props;

  /* Keep track fo dimensions to send to vega charts */
  const [{ width, height }, setDimensions] = React.useState({
    width: 0,
    height: 0,
  });

  return (
    <View
      width="size-4600"
      position="relative"
      padding="size-100"
      minHeight="size-2400"
      borderRadius="medium"
    >
      <Measure
        bounds
        onResize={contentRect => {
          if (contentRect.bounds) setDimensions(contentRect.bounds);
        }}
      >
        {({ measureRef }) => (
          <div ref={measureRef}>
            <View
              aria-label="data presentation preview"
              borderRadius="small"
              minHeight="size-3600"
            >
              {!!error && <MissingVizMessage error={error} />}
              {!!CurrentViz && dataViz && (
                <CurrentViz
                  dataViz={dataViz}
                  geog={geogIdentifier}
                  colorScheme={colorScheme}
                  vizHeight={height - 15}
                  vizWidth={width - 35}
                />
              )}
            </View>
          </div>
        )}
      </Measure>
    </View>
  );
});
