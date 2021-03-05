/**
 *
 * SubdomainSection
 *
 */

import React from 'react';
import { View } from '@react-spectrum/view';
import { Grid, minmax, repeat } from '@react-spectrum/layout';
import { Subdomain } from '../../types';
import { Heading } from '@adobe/react-spectrum';
import { Text } from '@react-spectrum/text';
import IndicatorCard from '../IndicatorCard';

interface Props {
  subdomain: Subdomain;
}

function SubdomainSection({ subdomain }: Props) {
  const { name, description, indicators } = subdomain;
  return (
    <View marginBottom="size-50">
      <Heading level={4} UNSAFE_style={{ marginBottom: '4px' }}>
        {name}
      </Heading>
      <View>
        <Text>{description}</Text>
      </View>
      <Grid
        columns={repeat('auto-fill', minmax('size-4600', '100%'))}
        gap="size-100"
        marginY="size-200"
      >
        {indicators.map(indicator => (
          <View key={indicator.slug}>
            <IndicatorCard indicator={indicator} />
          </View>
        ))}
      </Grid>
    </View>
  );
}

export default SubdomainSection;
