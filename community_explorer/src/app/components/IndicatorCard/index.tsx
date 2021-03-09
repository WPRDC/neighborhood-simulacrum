/**
 *
 * IndicatorCard
 *
 */
import React from 'react';
// import styled from 'styled-components/macro';
import { Indicator } from '../../types';
import { View } from '@react-spectrum/view';
import { Text, Grid, repeat, minmax } from '@adobe/react-spectrum';
import { DataViz } from '../../containers/DataViz';
import { Heading } from '@react-spectrum/text';

interface Props {
  indicator: Indicator;
}

function IndicatorCard({ indicator }: Props) {
  const {
    name,
    // slug,
    description,
    longDescription,
    // limitations,
    // importance,
    // source,
    // provenance,
    dataVizes,
  } = indicator;
  return (
    <View borderWidth="thin" backgroundColor="gray-50" padding="size-100">
      <View>
        <Heading level={5} UNSAFE_style={{ marginTop: 0, marginBottom: '4px' }}>
          {name}
        </Heading>
        <View paddingY="size-100">
          <Text>{description}</Text>
        </View>
      </View>
      <View>
        {dataVizes && (
          <Grid
            aria-label="Data visualizations"
            columns={repeat('auto-fill', minmax('size-1600', 'auto'))}
            rows={repeat('auto-fit', 'size-1600')}
            justifyContent="center"
            gap="size-100"
          >
            {dataVizes.map(dataViz => (
              <View
                borderRadius="xsmall"
                borderWidth="thin"
                borderColor="gray-400"
                padding="size-100"
                gridColumn={`auto / span ${dataViz.viewWidth}`}
                gridRow={`auto / span ${dataViz.viewHeight}`}
                overflow="auto"
              >
                <DataViz key={dataViz.slug} dataVizID={dataViz} />
              </View>
            ))}
          </Grid>
        )}
      </View>
      <View marginTop="size-100">
        <Text>{longDescription}</Text>
      </View>
    </View>
  );
}

export default IndicatorCard;
