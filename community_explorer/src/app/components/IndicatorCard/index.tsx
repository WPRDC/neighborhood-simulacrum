/**
 *
 * IndicatorCard
 *
 */
import React from 'react';
import { Indicator } from '../../types';
import {
  ActionButton,
  Button,
  Divider,
  Flex,
  Text,
  View,
} from '@adobe/react-spectrum';
import { Heading } from '@react-spectrum/text';
import More from '@spectrum-icons/workflow/More';
import { DataViz } from 'app/containers/DataViz';
import { DataVizVariant } from '../../containers/DataViz/types';

interface Props {
  indicator: Indicator;
  onExplore: () => void;
}

function IndicatorCard({ indicator, onExplore }: Props) {
  const {
    name,
    description,
    // slug,
    // longDescription,
    // limitations,
    // importance,
    // source,
    // provenance,
    dataVizes,
  } = indicator;

  function handleExplorePress() {
    onExplore();
  }

  // load first data viz (will eventually be some sort of master one or something)
  const primaryDataViz = !!dataVizes && dataVizes[0];

  return (
    <View
      borderRadius="medium"
      borderWidth="thin"
      borderColor="default"
      width="size-4600"
      position="relative"
      backgroundColor="gray-100"
    >
      <View
        borderTopStartRadius="medium"
        borderTopEndRadius="medium"
        height="size-2400"
        overflow="hidden"
        borderBottomColor="gray-800"
        borderBottomWidth="thin"
        backgroundColor="gray-200"
      >
        {primaryDataViz && (
          <DataViz
            variant={DataVizVariant.Preview}
            key={primaryDataViz.slug}
            dataVizID={primaryDataViz}
          />
        )}
      </View>
      <View padding="size-200">
        <View>
          {!!name && (
            <Flex>
              <View flexGrow={1}>
                <Heading level={3} UNSAFE_style={{ marginTop: 0 }}>
                  {name}
                </Heading>
              </View>
              <View>
                <ActionButton isQuiet>
                  <More />
                </ActionButton>
              </View>
            </Flex>
          )}
        </View>
        <View height="size-800">
          <Text>{description}</Text>
        </View>
      </View>

      <Divider marginX="size-200" size="S" />
      <View
        borderBottomStartRadius="small"
        borderBottomEndRadius="small"
        padding="size-200"
      >
        <Flex>
          <View />
          <View flexGrow={1} />
          <Button variant="primary" onPress={handleExplorePress}>
            Explore
          </Button>
        </Flex>
      </View>
    </View>
  );
}

export default IndicatorCard;
