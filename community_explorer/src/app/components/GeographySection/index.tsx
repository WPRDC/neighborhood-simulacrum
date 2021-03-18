/**
 *
 * GeographySection
 *
 */
import React from 'react';
import { Region } from '../../types';
import { useHistory } from 'react-router-dom';
import { DataChip } from '../DataChip';

import PeopleGroup from '@spectrum-icons/workflow/PeopleGroup';
import {
  Flex,
  Heading,
  Item,
  ProgressCircle,
  View,
  Text,
} from '@adobe/react-spectrum';
import { Breadcrumbs } from 'wprdc-components';

interface Props {
  region?: Region;
  regionIsLoading: boolean;
}

export function GeographySection(props: Props) {
  const { region, regionIsLoading } = props;
  const history = useHistory();

  function handleBreadcrumbClick(path: React.ReactText) {
    if (path === '__state' || typeof path !== 'string') {
      // fixme: '__state' check is hacky way of disabling first item
      return;
    }
    history.push(`/${path}`);
  }

  const breadCrumbItems = region && [
    <Item key="__state">Pennsylvania</Item>,
    ...region.hierarchy.map(h => (
      <Item key={`${h.regionType}/${h.regionID}`}>{h.title}</Item>
    )),
    <Item key="__current">
      <Heading
        level={2}
        margin="size-100"
        marginTop-="size-0"
        UNSAFE_style={{ fontSize: '5.2rem', lineHeight: '5.2rem' }}
      >
        {region.title}
      </Heading>
    </Item>,
  ];

  return (
    <View position="relative">
      {regionIsLoading && (
        <ProgressCircle
          isIndeterminate
          aria-label="Loading region details"
          size="M"
          position="absolute"
          top="size-200"
          right="size-200"
        />
      )}
      <View height="size-1600">
        {!!region ? (
          <Breadcrumbs isMultiline size="L" onAction={handleBreadcrumbClick}>
            {breadCrumbItems}
          </Breadcrumbs>
        ) : (
          <Text marginStart="size-200">Loading...</Text>
        )}
      </View>
      <View height="size-600">
        <Flex>
          <View>
            {!!region && region.population >= 0 && (
              <DataChip
                title="Population"
                icon={<PeopleGroup size="S" />}
                value={region.population}
              />
            )}
          </View>
          <View>
            {!!region && region.kidPopulation >= 0 && (
              <DataChip
                title="Population under 18"
                icon={<PeopleGroup size="S" />}
                value={region.kidPopulation}
              />
            )}
          </View>
        </Flex>
      </View>
    </View>
  );
}
