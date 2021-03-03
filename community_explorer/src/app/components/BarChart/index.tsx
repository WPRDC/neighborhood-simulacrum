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
} from 'recharts';
import { ChartData } from '../../types';

interface Props {
  data: ChartData;
  dataKey: string;
  barName: string;
}
export function BarChart(props: Props) {
  const { data, dataKey, barName } = props;
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
          layout="vertical"
          margin={{ left: 1, top: 1, right: 0, bottom: 1 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="name" width={200} interval={0} />
          <Tooltip />
          <Legend />
          <Bar name={barName} dataKey={dataKey} fill="#096c6f" />
        </RBarChart>
      </ResponsiveContainer>
    </View>
  );
}
