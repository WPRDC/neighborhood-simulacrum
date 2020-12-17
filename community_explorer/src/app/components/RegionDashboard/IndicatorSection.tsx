/**
 *
 * IndicatorSection
 *
 */

import React from 'react';

import { DataCard } from 'wprdc-components';

import { View } from '@react-spectrum/view';
import { DataViz } from '../../containers/DataViz';

function IndicatorSection({ indicator }) {
  const {
    name,
    // slug,
    description,
    longDescription,
    // limitations,
    // importance,
    source,
    // provenance,
    dataVizes,
  } = indicator;
  return (
    <DataCard
      title={name}
      note={description}
      description={longDescription}
      sources={[source]}
      headingLvl={5}
      viewStyleProps={{ marginBottom: 'size-150' }}
    >
      <View>
        {dataVizes &&
          dataVizes.map(dataViz => (
            <DataViz key={dataViz.slug} dataVizID={dataViz} />
          ))}
      </View>
    </DataCard>
  );
}

export default IndicatorSection;
