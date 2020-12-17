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

interface Props {
  subdomain: Subdomain;
}

function SubdomainSection({ subdomain }: Props) {
  const { name, description, indicators } = subdomain;
  return (
    <DataCard
      title={name}
      note={description}
      headingLvl={3}
      viewStyleProps={{ marginBottom: 'size-50' }}
    >
      <Grid
        columns={repeat('auto-fill', minmax('size-4600', '1fr'))}
        gap="size-100"
      >
        {indicators.map(indicator => (
          <View key={indicator.slug}>
            <IndicatorSection indicator={indicator} />
          </View>
        ))}
      </Grid>
    </DataCard>
  );
}

export default SubdomainSection;
