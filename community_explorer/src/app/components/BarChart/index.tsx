/**
 *
 * BarChart
 *
 */
import React from 'react';
import { View } from '@adobe/react-spectrum';

import {
  BarChart as RBarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  Bar,
  ResponsiveContainer,
  Cell,
} from 'recharts';

import { ChartData, DataVizDataPoint } from '../../types';
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
    <View
      padding="size-10"
      height="size-3600"
      minHeight="size-2000"
      maxHeight="size-3600"
    >
      <ResponsiveContainer width="100%" height="100%">
        <RBarChart
          data={data}
          layout={layout}
          margin={{ left: 1, top: 1, right: 0, bottom: 1 }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={!tickLine}
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
                cursor="pointer"
                fill={highlightIndex === index ? '#d83790' : '#096c6f'}
                key={`cell-${index}`}
              />
            ))}
          </Bar>
        </RBarChart>
      </ResponsiveContainer>
    </View>
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
