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

export const DataVizMini = memo((props: Props) => {
  const { dataViz, geogIdentifier, colorScheme, CurrentViz, error } = props;

  /* Keep track fo dimensions to send to vega charts */
  const [{ width, height }, setDimensions] = React.useState({
    width: 0,
    height: 0,
  });
  return (
    <View position="relative" padding="size-100" borderRadius="medium">
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
              maxWidth={!!error ? 'size-3000' : undefined}
            >
              {!!error && <MissingVizMessage error={error} />}
              {!error && !!CurrentViz && !!dataViz && !!geogIdentifier && (
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
