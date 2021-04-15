/**
 *
 * PieChart
 *
 * http://urbaninstitute.github.io/graphics-styleguide/
 */
import React from 'react';
import { ChartData, PieChartViz, VizProps } from '../../types';
import spec from './specs/donut';
import { Vega } from 'react-vega';
import { prepDataForVega } from '../../containers/DataViz/util';

interface Props extends VizProps<PieChartViz, ChartData> {}

export function PieChart(props: Props) {
  const { dataViz } = props;
  const data = prepDataForVega(dataViz.data);

  return <Vega spec={spec} data={data} />;
}
