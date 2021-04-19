import * as vega from 'vega';

const acrossGeogs: vega.Spec = {
  $schema: 'https://vega.github.io/schema/vega/v5.json',
  description: 'A simple bar chart across one or more series.',
  padding: 5,
  autosize: { type: 'fit', resize: true },
  signals: [
    {
      name: 'tooltip',
      value: {},
      on: [
        { events: 'rect:mouseover', update: 'datum' },
        { events: 'rect:mouseout', update: '{}' },
      ],
    },
  ],
  data: [
    {
      name: 'table',
      values: [],
    },
    {
      name: 'highlight',
      values: [],
    },
  ],
  scales: [
    {
      name: 'geogScale',
      type: 'band',
      domain: {
        data: 'table',
        field: 'geog',
        sort: { op: 'median', field: 'value', order: 'ascending' },
      },
      range: 'width',
      padding: 0.15,
    },
    {
      name: 'valueScale',
      domain: { data: 'table', field: 'value' },
      nice: true,
      range: 'height',
    },
  ],
  axes: [
    {
      orient: 'bottom',
      scale: 'geogScale',
      labelFont: 'Helvetica Neue',
      ticks: false,
      labels: true,
      labelAngle: 45,
      labelAlign: 'left',
      encode: {
        labels: {
          update: {
            text: { signal: "datum.value == 'Pittsburgh' ? datum.value : ''" },
          },
        },
      },
    },
    {
      orient: 'left',
      scale: 'valueScale',
      labelFont: 'Helvetica Neue',
      ticks: false,
      labelPadding: 0,
      grid: true,
      domain: false,
    },
  ],
  marks: [
    {
      name: 'bars',
      from: { data: 'table' },
      type: 'rect',
      encode: {
        enter: {
          tooltip: {
            signal: "datum.geog + ': ' + format(datum.value, '1,')",
          },
          x: { scale: 'geogScale', field: 'geog' },
          width: { scale: 'geogScale', band: 1 },
          y: { scale: 'valueScale', field: 'value' },
          y2: { scale: 'valueScale', value: 0 },
          cornerRadiusTopLeft: { value: 2 },
          cornerRadiusTopRight: { value: 2 },
        },
        update: {
          fill: [
            {
              test: "indata('highlight', 'highlight', datum.geog)",
              value: '#F2B705',
            },
            { value: '#96C6D9' },
          ],
          stroke: { value: '' },
        },
        hover: {
          stroke: { value: 'black' },
        },
      },
    },
  ],
};

export default acrossGeogs;
