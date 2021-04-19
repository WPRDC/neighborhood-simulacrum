/**
 *
 * BarChart
 *
 */
import React from 'react';
import { specs } from './specs';
import { BarChartViz, ChartData, GeogIdentifier, VizProps } from '../../types';
import { PlainObject, Vega } from 'react-vega';
import { prepDataForVega } from '../../containers/DataViz/util';
import * as vega from 'vega';

interface Props extends VizProps<BarChartViz, ChartData> {}

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

function getExtraData(dataViz: BarChartViz, geog: GeogIdentifier): PlainObject {
  if (dataViz.acrossGeogs) {
    return { highlight: { highlight: geog.geogID } };
  }
  return {};
}

function getSpec(dataViz: BarChartViz): vega.Spec {
  if (dataViz.acrossGeogs) return specs.acrossGeogs;
  if (dataViz.layout === 'column') return specs.column;
  return specs.bar;
}
