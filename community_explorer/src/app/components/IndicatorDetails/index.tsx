/**
 *
 * IndicatorDetails
 *
 */
import React from 'react';
import {
  Divider,
  Grid,
  Heading,
  minmax,
  repeat,
  Text,
  View,
} from '@adobe/react-spectrum';
import { DataViz } from '../../containers/DataViz';
import { DataVizID, DataVizType, Indicator } from '../../types';
import { Breadcrumbs } from 'wprdc-components';
import { DataVizVariant } from '../../containers/DataViz/types';

interface Props {
  indicator: Indicator;
  breadCrumbItems: JSX.Element[];
  onBreadcrumbClick: (path: React.ReactText) => void;
}

const BLURBS = [DataVizType.BigValue, DataVizType.Sentence];

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
      <Divider marginX="size-100" />
      {!!blurbs.length && (
        <View padding="size-100">
          <Heading level={4}>Quick Facts</Heading>
          {blurbs.map(blurb => (
            <DataViz dataVizID={blurb} variant={DataVizVariant.Blurb} />
          ))}
        </View>
      )}

      {!!vizes && (
        <View padding="size-100">
          <Heading level={4}>Data Visualizations</Heading>
          <Grid
            columns={repeat('auto-fit', minmax('size-3600', 'size-6000'))}
            rows="auto"
            gap="size-500"
          >
            {vizes.map(dataViz => (
              <View
                key={dataViz.slug}
                maxWidth="size-6000"
                minHeight="size-2400"
              >
                <DataViz dataVizID={dataViz} />
              </View>
            ))}
          </Grid>
        </View>
      )}
    </View>
  );
}

function splitVizes(dataVizes: DataVizID[]) {
  const init: { blurbs: DataVizID[]; vizes: DataVizID[] } = {
    blurbs: [],
    vizes: [],
  };

  return dataVizes.reduce((splitRecord, dataViz) => {
    if (BLURBS.includes(dataViz.vizType)) {
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
