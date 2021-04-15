import * as vega from 'vega';

const ColumnChartSpec: vega.Spec = {
  $schema: 'https://vega.github.io/schema/vega/v5.json',
  description: 'A column chart with one ore more series ',

  width: 600,
  height: 300,
  padding: 5,

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

  scales: [
    {
      name: 'xscale',
      type: 'band',
      domain: { data: 'table', field: 'category' },
      range: 'width',
      padding: 0.15,
      round: true,
    },
    {
      name: 'yscale',
      domain: { data: 'table', field: 'value' },
      nice: true,
      range: 'height',
    },
    {
      name: 'color',
      type: 'ordinal',
      domain: { data: 'table', field: 'position' },
      range: {
        scheme: ['#D0E9F2', '#96C6D9', '#3F89A6', '#204959', '#0B1F26'],
      },
    },
  ],

  axes: [
    {
      orient: 'left',
      scale: 'yscale',
      labelFont: 'Helvetica Neue',
      ticks: false,
      labelPadding: 4,
      grid: true,
      domain: false,
    },
    {
      orient: 'bottom',
      scale: 'xscale',
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
          groupby: 'category',
        },
      },

      encode: {
        enter: {
          x: { scale: 'xscale', field: 'category' },
        },
      },

      signals: [{ name: 'width', update: "bandwidth('xscale')" }],

      scales: [
        {
          name: 'pos',
          type: 'band',
          range: 'width',
          domain: { data: 'facet', field: 'position' },
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
                signal: "'Value: ' + format(datum.value, '1')",
              },
              x: { scale: 'pos', field: 'position' },
              width: { scale: 'pos', band: 1 },
              y: { scale: 'yscale', field: 'value' },
              y2: { scale: 'yscale', value: 0 },
              fill: { scale: 'color', field: 'position' },
            },
          },
        },
      ],
    },
  ],
};

export default ColumnChartSpec;
