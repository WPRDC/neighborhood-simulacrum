/**
 *
 * DataVizCard
 *
 */
import React from 'react';
import {
  ActionButton,
  Button,
  Flex,
  Heading,
  MenuTrigger,
  StatusLight,
  Text,
  View,
} from '@adobe/react-spectrum';
import Measure from 'react-measure';
import { VizWrapperProps } from '../../types';
import More from '@spectrum-icons/workflow/More';
import { SourceList } from '../SourceList';
import { LoadingMessage } from '../LoadingMessage';
import { MissingVizMessage } from '../MissingVizMessage';

interface Props extends VizWrapperProps {}

export function DataVizCard(props: Props) {
  const {
    dataViz,
    geogIdentifier,
    colorScheme,
    CurrentViz,
    isLoading,
    menu,
    onExplore,
    error,
  } = props;
  const { name, description } = dataViz || {};

  /* Keep track fo dimensions to send to vega charts */
  const [{ width, height }, setDimensions] = React.useState({
    width: 0,
    height: 0,
  });
  return (
    <View
      borderRadius="medium"
      borderWidth="thin"
      borderColor="default"
      maxWidth="size-6000"
      position="relative"
      backgroundColor="gray-100"
    >
      <View
        borderTopStartRadius="medium"
        borderTopEndRadius="medium"
        padding="size-200"
        overflow="hidden"
        backgroundColor="gray-100"
      >
        {!!name && (
          <Flex alignItems="center">
            <View flexGrow={1}>
              <Heading level={3} UNSAFE_style={{ margin: 0 }}>
                {name}
              </Heading>
            </View>
            <View>
              <MenuTrigger>
                <ActionButton isQuiet>
                  <More />
                </ActionButton>
                {menu}
              </MenuTrigger>
            </View>
          </Flex>
        )}
        <View>
          <Text>
            {description ||
              'Glos fatalis apolloniates est. Danistas sunt lacteas de noster calceus.'}
          </Text>
        </View>
      </View>
      <View borderYWidth="thin" borderYColor="gray-400">
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
                minHeight="size-3600"
              >
                {isLoading && <LoadingMessage />}
                {!!error && <MissingVizMessage error={error} />}
                {!isLoading &&
                  !!CurrentViz &&
                  !!dataViz &&
                  !!geogIdentifier && (
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
      <View
        padding="size-200"
        backgroundColor="gray-100"
        borderBottomStartRadius="medium"
        borderBottomEndRadius="medium"
      >
        <Flex>
          <View flexGrow={1}>
            <StatusLight variant="neutral">Static Dataset</StatusLight>
          </View>
          <View>
            <Button variant="cta" onPress={onExplore}>
              Learn More
            </Button>
          </View>
        </Flex>
      </View>
    </View>
  );
}
