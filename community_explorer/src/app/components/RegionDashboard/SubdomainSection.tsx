/**
 *
 * SubdomainSection
 *
 */

import React from 'react';
import { View } from '@react-spectrum/view';
import { DataCard } from 'wprdc-components';
import IndicatorSection from './IndicatorSection';
import { Grid, minmax, repeat } from '@react-spectrum/layout';
import { Subdomain } from '../../types';
import { Heading } from '@adobe/react-spectrum';
import { Text } from '@react-spectrum/text';

interface Props {
  subdomain: Subdomain;
}

function SubdomainSection({ subdomain }: Props) {
  const { name, description, indicators } = subdomain;
  return (
    <View marginBottom="size-50">
      <Heading level={4}>{name}</Heading>
      <Text>{description}</Text>
      <Grid
        columns={repeat('auto-fill', minmax('size-4600', '100%'))}
        gap="size-100"
      >
        {indicators.map(indicator => (
          <View key={indicator.slug}>
            <IndicatorSection indicator={indicator} />
          </View>
        ))}
      </Grid>
    </View>
  );
}

export default SubdomainSection;
