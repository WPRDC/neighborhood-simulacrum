import * as vega from 'vega';

const column: vega.Spec = {
  $schema: 'https://vega.github.io/schema/vega/v5.json',
  description: 'A simple bar chart across one or more series.',
  padding: 5,
  width: 600,
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
      name: 'variableScale',
      type: 'band',
      domain: { data: 'table', field: 'variable' },
      range: 'width',
      padding: 0.15,
      round: true,
    },
    {
      name: 'valueScale',
      domain: { data: 'table', field: 'value' },
      nice: true,
      range: 'height',
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
      scale: 'variableScale',
      labelFont: 'Helvetica Neue',
      ticks: false,
      labelPadding: 4,
    },
    {
      orient: 'left',
      scale: 'valueScale',
      labelFont: 'Helvetica Neue',
      ticks: false,
      labelPadding: 4,
      grid: true,
      domain: false,
    },
  ],
  marks: [
    {
      type: 'group',
      from: {
        facet: { data: 'table', name: 'facet', groupby: 'variable' },
      },
      encode: { enter: { x: { scale: 'variableScale', field: 'variable' } } },
      signals: [{ name: 'height', update: "bandwidth('variableScale')" }],
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
              tooltip: { signal: "'Value: ' + format(datum.value, '1')" },
              x: { scale: 'pos', field: 'timeSeries' },
              width: { scale: 'pos', band: 1 },
              y: { scale: 'valueScale', field: 'value' },
              y2: { scale: 'valueScale', value: 0 },
              fill: { scale: 'color', field: 'timeSeries' },
            },
          },
        },
      ],
    },
  ],
};

export default column;
