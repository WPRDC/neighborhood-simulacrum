import * as vega from 'vega';

const donut: vega.Spec = {
  $schema: 'https://vega.github.io/schema/vega/v5.json',
  description: 'A simple bar chart across one or more series.',
  padding: 5,
  width: 300,
  height: 180,
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
  data: [{ name: 'table', values: [] }],
  scales: [
    {
      name: 'yscale',
      type: 'band',
      domain: { data: 'table', field: 'variable' },
      range: 'height',
      padding: 0.15,
      round: true,
    },
    {
      name: 'xscale',
      domain: { data: 'table', field: 'value' },
      nice: true,
      range: 'width',
    },
    {
      name: 'color',
      type: 'ordinal',
      domain: { data: 'table', field: 'timeSeries' },
      range: {
        scheme: ['#D0E9F2', '#96C6D9', '#3F89A6', '#204959', '#0B1F26'],
      },
    },
  ],

  axes: [
    {
      orient: 'bottom',
      scale: 'xscale',
      labelFont: 'Helvetica Neue',
      ticks: false,
      labelPadding: 4,
      grid: true,
      domain: false,
    },
    {
      orient: 'left',
      scale: 'yscale',
      labelFont: 'Helvetica Neue',
      ticks: false,
      labelPadding: 4,
    },
  ],

  marks: [
    {
      type: 'group',

      from: {
        facet: {
          data: 'table',
          name: 'facet',
          groupby: 'variable',
        },
      },

      encode: {
        enter: {
          y: { scale: 'yscale', field: 'variable' },
        },
      },

      signals: [{ name: 'height', update: "bandwidth('yscale')" }],

      scales: [
        {
          name: 'pos',
          type: 'band',
          range: 'height',
          domain: { data: 'facet', field: 'timeSeries' },
        },
      ],

      marks: [
        {
          name: 'bars',
          from: { data: 'facet' },
          type: 'rect',
          encode: {
            enter: {
              tooltip: {
                signal: "datum.variable + ': ' + format(datum.value, '1,')",
              },
              y: { scale: 'pos', field: 'timeSeries' },
              height: { scale: 'pos', band: 1 },
              x: { scale: 'xscale', field: 'value' },
              x2: { scale: 'xscale', value: 0 },
              fill: { scale: 'color', field: 'timeSeries' },
            },
          },
        },
      ],
    },
  ],
};

export default donut;
