/**
 *
 * LineChart
 *
 */
import React from 'react';
import { ChartData, LineChartViz, VizProps } from '../../types';
import spec from '../BarChart/specs/bar';
import { prepDataForVega } from '../../containers/DataViz/util';
import { Vega } from 'react-vega';

interface Props extends VizProps<LineChartViz, ChartData> {}

export function LineChart(props: Props) {
  const { dataViz } = props;
  const data = prepDataForVega(dataViz.data);
  return <Vega spec={spec} data={data} />;
}
