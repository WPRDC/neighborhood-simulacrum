/**
 *
 * BarChart
 *
 */
import React from 'react';
import { specs } from './specs';
import { TabularData, GeogIdentifier, VizProps, ChartViz } from '../../types';
import { PlainObject, Vega } from 'react-vega';
import { prepDataForVega } from '../../containers/DataViz/util';
import * as vega from 'vega';

interface Props extends VizProps<ChartViz, TabularData> {}

export function BarChart(props: Props) {
  const { dataViz, geog, vizHeight, vizWidth } = props;
  const data = prepDataForVega(dataViz);
  const spec = getSpec(dataViz);
  const extraData = getExtraData(dataViz, geog);
  console.debug(dataViz);
  console.debug(extraData);

  // todo: in prepDataForVega, get the labels for the variable and time slugs provided in the data.

  return (
    <Vega
      spec={spec}
      data={{ ...data, ...extraData }}
      height={vizHeight}
      width={vizWidth}
      actions={false}
    />
  );
}

/**
 * Add data tables for styling.
 *
 * @param dataViz
 * @param geog
 */
function getExtraData(dataViz: ChartViz, geog: GeogIdentifier): PlainObject {
  // used in vega spec to apply highlight style
  let highlight;
  // lookup table for labels
  let labels = dataViz.variables.map(v => ({ var: v.slug, label: v.name }));

  if (dataViz.staticOptions.acrossGeogs) {
    highlight = { highlight: geog.geogID };
    return { highlight, labels };
  }

  return { labels };
}

function getSpec(dataViz: ChartViz): vega.Spec {
  if (dataViz.staticOptions.acrossGeogs) return specs.acrossGeogs;
  // if (dataViz.layout === 'column') return specs.column;

  return specs.bar;
}
