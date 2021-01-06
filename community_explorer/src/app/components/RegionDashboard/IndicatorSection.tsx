/**
 *
 * IndicatorSection
 *
 */

import React from 'react';

import { DataCard } from 'wprdc-components';

import { View } from '@react-spectrum/view';
import { DataViz } from '../../containers/DataViz';
import { DataVizResourceType, Indicator } from '../../types';
import { Content, Item } from '@adobe/react-spectrum';
import { Tabs } from '@react-spectrum/tabs';

import TableIcon from '@spectrum-icons/workflow/Table';
import PieIcon from '@spectrum-icons/workflow/GraphDonut';
// import BarGraphIcon from '@spectrum-icons/workflow/GraphBarHorizontal'
import MapIcon from '@spectrum-icons/workflow/MapView';

interface Props {
  indicator: Indicator;
}

function IndicatorSection({ indicator }: Props) {
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
    <DataCard
      title={name}
      note={description}
      description={longDescription}
      headingLvl={5}
      viewStyleProps={{ marginBottom: 'size-150', backgroundColor: 'gray-50' }}
    >
      <View>
        <Tabs aria-label="Data visualizations" isQuiet>
          {dataVizes &&
            dataVizes.map(dataViz => (
              <Item title={getTitle(dataViz)} key={dataViz.slug}>
                <Content marginTop="size-250" marginStart="size-125">
                  <View overflow="auto" maxHeight="size-3000">
                    <DataViz key={dataViz.slug} dataVizID={dataViz} />
                  </View>
                </Content>
              </Item>
            ))}
        </Tabs>
      </View>
    </DataCard>
  );
}

function getTitle(dataViz) {
  const mapping: Record<DataVizResourceType, React.ReactNode> = {
    [DataVizResourceType.Table]: (
      <>
        <TableIcon size="S" /> Table
      </>
    ),
    [DataVizResourceType.PieChart]: (
      <>
        <PieIcon size="S" /> Donut Chart
      </>
    ),
    [DataVizResourceType.Sentence]: <>Story</>,
    [DataVizResourceType.BigValue]: <>Big Value</>,
    [DataVizResourceType.MiniMap]: (
      <>
        <MapIcon size="S" /> Map
      </>
    ),
  };
  return mapping[dataViz.resourcetype];
}

export default IndicatorSection;
