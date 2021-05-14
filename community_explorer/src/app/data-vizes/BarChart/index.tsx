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
  const data = prepDataForVega(dataViz.data);
  const spec = getSpec(dataViz);
  const extraData = getExtraData(dataViz, geog);

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

function getExtraData(dataViz: ChartViz, geog: GeogIdentifier): PlainObject {
  if (dataViz.staticOptions.acrossGeogs) {
    return { highlight: { highlight: geog.geogID } };
  }
  return {};
}

function getSpec(dataViz: ChartViz): vega.Spec {
  if (dataViz.staticOptions.acrossGeogs) return specs.acrossGeogs;
  // if (dataViz.layout === 'column') return specs.column;

  return specs.bar;
}
