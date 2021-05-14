/**
 *
 * DataVizDetails
 *
 */
import React from 'react';
import { Text, View } from '@adobe/react-spectrum';
import Measure from 'react-measure';
import { VizWrapperProps } from '../../types';
import { SourceList } from '../SourceList';
import { LoadingMessage } from '../LoadingMessage';
import { Breadcrumbs } from 'wprdc-components';
import { MissingVizMessage } from '../MissingVizMessage';

interface Props extends VizWrapperProps {}

export function DataVizDetails(props: Props) {
  const {
    dataViz,
    geogIdentifier,
    colorScheme,
    CurrentViz,
    isLoading,
    breadcrumbs,
    onBreadcrumbClick,
    menu,
    error,
  } = props;
  const { name, description } = dataViz || {};
  /* Keep track fo dimensions to send to vega charts */
  const [{ width, height }, setDimensions] = React.useState({
    width: 0,
    height: 0,
  });

  return (
    <View position="relative">
      <Breadcrumbs isMultiline size="L" onAction={onBreadcrumbClick}>
        {breadcrumbs}
      </Breadcrumbs>
      <View padding="size-200" paddingTop="size-50">
        <View>
          <Text>{description}</Text>
        </View>
      </View>
      <Measure
        bounds
        onResize={contentRect => {
          if (contentRect.bounds) setDimensions(contentRect.bounds);
        }}
      >
        {({ measureRef }) => (
          <div ref={measureRef}>
            <View
              aria-label="data presentation"
              minHeight="size-5000"
              height="size-5000"
              borderWidth="thin"
              backgroundColor="gray-100"
            >
              {!!error && <MissingVizMessage error={error} />}
              {isLoading && <LoadingMessage />}
              {!isLoading && !!CurrentViz && !!dataViz && (
                <CurrentViz
                  dataViz={dataViz}
                  geog={geogIdentifier}
                  colorScheme={colorScheme}
                  vizHeight={height - 15}
                  vizWidth={width - 15}
                />
              )}
            </View>
          </div>
        )}
      </Measure>
      <View paddingStart="size-200" paddingY="size-0">
        {!!dataViz && !!dataViz.sources && (
          <SourceList sources={dataViz.sources} colorScheme={colorScheme} />
        )}
      </View>
    </View>
  );
}
