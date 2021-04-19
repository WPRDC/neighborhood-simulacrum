/**
 *
 * IndicatorDetails
 *
 */
import React from 'react';
import { Grid, minmax, repeat, Text, View } from '@adobe/react-spectrum';
import { DataViz } from '../../containers/DataViz';
import { DataVizID, DataVizResourceType, Indicator } from '../../types';
import { Breadcrumbs } from 'wprdc-components';
import { DataVizVariant } from '../../containers/DataViz/types';

interface Props {
  indicator: Indicator;
  breadCrumbItems: JSX.Element[];
  onBreadcrumbClick: (path: React.ReactText) => void;
}

const BLURBS = [DataVizResourceType.BigValue, DataVizResourceType.Sentence];

export function IndicatorDetails({
  indicator,
  breadCrumbItems,
  onBreadcrumbClick,
}: Props) {
  const { description, dataVizes } = indicator;
  const { blurbs, vizes } = splitVizes(dataVizes);
  return (
    <View marginBottom="size-50">
      <Breadcrumbs isMultiline size="L" onAction={onBreadcrumbClick}>
        {breadCrumbItems}
      </Breadcrumbs>
      <View padding="size-100" marginBottom="size-100">
        <Text>{description}</Text>
      </View>
      <View padding="size-100">
        {blurbs.map(blurb => (
          <DataViz dataVizID={blurb} variant={DataVizVariant.Blurb} />
        ))}
      </View>

      <Grid
        columns={repeat('auto-fit', minmax('size-3600', 'size-6000'))}
        rows="auto"
        gap="size-500"
      >
        {vizes.map(dataViz => (
          <View key={dataViz.slug} maxWidth="size-6000" minHeight="size-2400">
            <DataViz dataVizID={dataViz} />
          </View>
        ))}
      </Grid>
    </View>
  );
}

function splitVizes(dataVizes: DataVizID[]) {
  const init: { blurbs: DataVizID[]; vizes: DataVizID[] } = {
    blurbs: [],
    vizes: [],
  };

  return dataVizes.reduce((splitRecord, dataViz) => {
    if (BLURBS.includes(dataViz.resourcetype)) {
      return {
        blurbs: [...splitRecord.blurbs, dataViz],
        vizes: splitRecord.vizes,
      };
    }
    return {
      blurbs: splitRecord.blurbs,
      vizes: [...splitRecord.vizes, dataViz],
    };
  }, init);
}
