/**
 *
 * GeographySection
 *
 */
import React from 'react';
import { Geog } from '../../types';
import { useHistory } from 'react-router-dom';
import { DataChip } from '../DataChip';

import PeopleGroup from '@spectrum-icons/workflow/PeopleGroup';
import {
  Flex,
  Heading,
  Item,
  ProgressCircle,
  Text,
  View,
} from '@adobe/react-spectrum';
import { Breadcrumbs } from 'wprdc-components';

interface Props {
  geog?: Geog;
  geogIsLoading: boolean;
}

export function GeographySection(props: Props) {
  const { geog, geogIsLoading } = props;
  const history = useHistory();

  function handleBreadcrumbClick(path: React.ReactText) {
    if (path === '__state' || typeof path !== 'string') {
      // fixme: '__state' check is hacky way of disabling first item
      return;
    }
    history.push(`/${path}`);
  }

  const breadCrumbItems = geog && [
    <Item key="__state">Pennsylvania</Item>,
    ...geog.hierarchy.map(h => (
      <Item key={`${h.geogType}/${h.geogID}`}>{h.title}</Item>
    )),
    <Item key="__current">
      <Heading
        level={2}
        margin="size-100"
        marginTop-="size-0"
        UNSAFE_style={{ fontSize: '5.2rem', lineHeight: '5.2rem' }}
      >
        {geog.title}
      </Heading>
    </Item>,
  ];

  return (
    <View position="relative" padding="size-200">
      {geogIsLoading && (
        <ProgressCircle
          isIndeterminate
          aria-label="Loading geog details"
          size="M"
          position="absolute"
          top="size-200"
          right="size-200"
        />
      )}
      <View height="size-1600">
        {!!geog ? (
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
            {!!geog && geog.population >= 0 && (
              <DataChip
                title="Population"
                icon={<PeopleGroup size="S" />}
                value={geog.population}
              />
            )}
          </View>
          <View>
            {!!geog && geog.kidPopulation >= 0 && (
              <DataChip
                title="Population under 18"
                icon={<PeopleGroup size="S" />}
                value={geog.kidPopulation}
              />
            )}
          </View>
        </Flex>
      </View>
    </View>
  );
}
