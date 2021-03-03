/**
 *
 * PieChart
 *
 * http://urbaninstitute.github.io/graphics-styleguide/
 */
import React from 'react';

import {
  PieChart as RPieChart,
  Pie,
  ResponsiveContainer,
  Cell,
  Legend,
  Tooltip,
} from 'recharts';
import { View } from '@adobe/react-spectrum';
import { ChartData } from '../../types';

interface Props {
  data: ChartData;
  dataKey: string;
}

export function PieChart(props: Props) {
  return (
    <View padding="size-10" height="size-2400" minHeight="size-2400">
      <ResponsiveContainer>
        <RPieChart>
          <Pie
            {...props}
            innerRadius={30}
            outerRadius={70}
            label={renderCustomizedLabel}
            labelLine={false}
            paddingAngle={5}
            startAngle={0}
            endAngle={180}
          >
            {props.data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
              />
            ))}
          </Pie>
          <Tooltip />
          <Legend verticalAlign="top" height={36} />
        </RPieChart>
      </ResponsiveContainer>
    </View>
  );
}

const RADIAN = Math.PI / 180;

const renderCustomizedLabel = ({
  cx,
  cy,
  midAngle,
  innerRadius,
  outerRadius,
  percent,
  index,
}) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);
  // @ts-ignore
  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor={x > cx ? 'start' : 'end'}
      dominantBaseline="central"
    >
      {percent.toLocaleString(undefined, { style: 'percent' })}
    </text>
  ) as SVGElement;
};

const COLORS = [
  '#2680eb',
  '#e34850',
  '#e68619',
  '#2d9d78',
  '#0d66d0',
  '#c9252d',
  '#cb6f10',
  '#12805c',
];
