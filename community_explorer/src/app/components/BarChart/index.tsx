/**
 *
 * BarChart
 *
 */
import React from 'react';

import {
  Bar,
  BarChart as RBarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { ChartData } from '../../types';
import { BaseAxisProps, LayoutType } from 'recharts/types/util/types';

interface Props {
  data: ChartData;
  dataKey: string;
  barName: string;
  layout: LayoutType;
  highlightIndex?: number;
}

interface AxisProps extends BaseAxisProps {
  width?: number;
  interval?: number;
}

export function BarChart(props: Props) {
  const { data, dataKey, barName, layout, highlightIndex } = props;
  // handle axis flipping based
  let axesProps: AxisProps[] = [
    { type: 'number' },
    { type: 'category', dataKey: 'name', width: 200, interval: 0 },
  ];
  if (layout === 'horizontal') {
    axesProps.reverse();
  }
  const [xAxisProps, yAxisProps] = axesProps;
  const tickLine = highlightIndex === undefined;
  return (
    <ResponsiveContainer width="100%" height="100%">
      <RBarChart
        data={data}
        layout={layout}
        margin={{ left: 1, top: 1, right: 0, bottom: 1 }}
      >
        <CartesianGrid
          strokeDasharray={tickLine ? '3 3' : undefined}
          vertical={tickLine}
          horizontal={!tickLine}
        />
        <XAxis
          {...xAxisProps}
          tickFormatter={tickFormatter(highlightIndex)}
          tickLine={tickLine}
        />
        <YAxis {...yAxisProps} />
        <Tooltip />
        <Legend />
        <Bar name={barName} dataKey={dataKey}>
          {data.map((entry, index) => (
            <Cell
              fill={highlightIndex === index ? '#d83790' : '#096c6f'}
              key={`cell-${index}`}
            />
          ))}
        </Bar>
      </RBarChart>
    </ResponsiveContainer>
  );
}

const tickFormatter = highlightIndex => {
  if (highlightIndex === undefined) return undefined;
  return (value, index) => {
    if (highlightIndex === index) {
      return value;
    }
    return '';
  };
};
