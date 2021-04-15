/**
 *
 * BarChart
 *
 */
import React from 'react';
import { specs } from './specs';
import { ChartData, BarChartViz, VizProps } from '../../types';
import { Vega } from 'react-vega';
import { prepDataForVega } from '../../containers/DataViz/util';
import vega from 'vega';

interface Props extends VizProps<BarChartViz, ChartData> {}

export function BarChart(props: Props) {
  const { dataViz, vizHeight, vizWidth } = props;
  const data = prepDataForVega(dataViz.data);
  const spec = getSpec(dataViz);

  console.log({ vizHeight, vizWidth });

  return (
    <Vega
      spec={spec}
      data={data}
      height={vizHeight}
      width={vizWidth}
      actions={false}
    />
  );
}

function getSpec(dataViz: BarChartViz): vega.Spec {
  if (dataViz.acrossGeogs) return specs.acrossGeogs;
  if (dataViz.layout === 'column') return specs.column;
  return specs.bar;
}
