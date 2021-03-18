/**
 *
 * IndicatorDetails
 *
 */
import React from 'react';
import { Text, View, Grid, repeat } from '@adobe/react-spectrum';
import { DataViz } from '../../containers/DataViz';
import { Indicator } from '../../types';
import { Breadcrumbs } from 'wprdc-components';

interface Props {
  indicator: Indicator;
  breadCrumbItems: JSX.Element[];
  onBreadcrumbClick: (path: React.ReactText) => void;
}

export function IndicatorDetails({
  indicator,
  breadCrumbItems,
  onBreadcrumbClick,
}: Props) {
  const { description, dataVizes } = indicator;
  return (
    <View marginBottom="size-50">
      <Breadcrumbs isMultiline size="L" onAction={onBreadcrumbClick}>
        {breadCrumbItems}
      </Breadcrumbs>
      <View padding="size-100" marginBottom="size-100">
        <Text>{description}</Text>
      </View>
      <Grid
        columns={repeat('auto-fit', 'size-6000')}
        rows="auto"
        gap="size-250"
      >
        {dataVizes.map(dataViz => (
          <View key={dataViz.slug} maxWidth="size-6000">
            <DataViz dataVizID={dataViz} />
          </View>
        ))}
      </Grid>
    </View>
  );
}
