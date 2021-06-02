import { GeographyType } from '../../types';
import theme from './theme';

export function makeLayers(geogType: GeographyType) {
  return [
    {
      id: `${geogType}/hover`,
      type: 'fill',
      source: geogType,
      'source-layer': geogType,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.hoverColor,
      },
      filter: ['==', 'geogid', ''],
    },
    {
      id: `${geogType}/selected`,
      type: 'fill',
      source: geogType,
      'source-layer': geogType,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.standard,
        'fill-color': theme.polygons.selectedColor,
      },
      filter: ['==', 'geogid', ''],
    },
    {
      id: `${geogType}/borders`,
      type: 'line',
      source: geogType,
      'source-layer': geogType,
      layout: {
        'line-join': 'round',
      },
      paint: {
        'line-width': theme.polygons.lineWidth.dense,
        'line-opacity': theme.polygons.lineOpacity.standard,
        'line-color': theme.polygons.lineColor,
      },
    },
    {
      id: `${geogType}/fill`,
      type: 'fill',
      source: geogType,
      'source-layer': geogType,
      layout: {},
      paint: {
        'fill-opacity': theme.polygons.fillOpacity.selection,
        'fill-color': theme.polygons.fillColor,
      },
    },
  ];
}
export default makeLayers;
