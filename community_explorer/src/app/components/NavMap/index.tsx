/**
 *
 * NavMap
 *
 */
import React from 'react';
import { GeoLayer } from '../../containers/Explorer/types';

import { fetchCartoVectorSource, LayerOptions, Map } from 'wprdc-components';
import { LayerProps, SourceProps } from 'react-map-gl';

import menuLayers from './menuLayers';
import { MAPBOX_API_TOKEN } from '../../settings';

interface Props {
  menuLayer: GeoLayer;
  onClick: (selection: {
    regionType: string;
    regionID: string;
    name: string;
  }) => void;
}

export function NavMap(props: Props) {
  const { menuLayer, onClick } = props;
  // internal state
  const [mbSource, setMbSource] = React.useState<SourceProps | undefined>(
    undefined,
  );
  const [mbLayers, setMbLayers] = React.useState<LayerOptions[]>([]);
  const [interactiveLayerIds, setInteractiveLayerIds] = React.useState<
    string[]
  >([]);
  const [hoveredFilter, setHoveredFilter] = React.useState<any[]>(
    clearLayerFilter(),
  );
  const [selectedFilter, setSelectedFilter] = React.useState<any[]>(
    clearLayerFilter(),
  );

  // todo: on init, fetch all of the carto data
  React.useEffect(() => {
    if (menuLayer) {
      const usedLayer = menuLayers[menuLayer.slug];
      const { source, layers } = usedLayer || {};
      setMbLayers(layers);
      setMbSource(undefined);
      setInteractiveLayerIds(
        layers
          .filter(layerFilter)
          .filter(l => !!l.id)
          .map(l => l.id),
      );

      fetchCartoVectorSource(
        usedLayer.slug,
        source.sql,
        // eslint-disable-next-line no-console
      ).then(receiveMbSource, err => console.warn('CARTO', err));
    }
  }, [menuLayer]);

  function receiveMbSource(sourceData) {
    setMbSource(sourceData);
  }

  function handleHover(e) {
    if (e.features.length) {
      const { regionid: regionID } = e.features[0].properties;
      setHoveredFilter(filterLayerByRegionID(regionID));
    } else {
      setHoveredFilter(clearLayerFilter());
    }
  }

  function handleClick(e) {
    if (e && e.features && e.features.length) {
      const {
        regiontype: regionType,
        regionid: regionID,
        name,
      } = e.features[0].properties;
      setSelectedFilter(filterLayerByRegionID(regionID));
      onClick({ regionType, regionID, name });
    } else {
      setSelectedFilter(clearLayerFilter());
    }
  }

  const mapSources = mbSource ? [mbSource] : undefined;

  const mapLayers = filteredLayers(mbLayers, hoveredFilter, selectedFilter);

  return (
    <Map
      width="100%"
      height="100%"
      interactiveLayerIds={mbSource ? interactiveLayerIds : []}
      onHover={handleHover}
      onClick={handleClick}
      mapboxApiAccessToken={MAPBOX_API_TOKEN}
      sources={mapSources}
      layers={mapLayers}
    />
  );
}

const layerType = l => l.id.split('/')[1];

const layerFilter = l => layerType(l) === 'fill';

function filterLayerByRegionID(regionID: string) {
  return ['==', 'regionid', regionID];
}

function clearLayerFilter() {
  return ['==', 'regionid', 'w00t'];
}

function filteredLayers(
  layers: LayerOptions[],
  hoveredFilter,
  selectedFilter,
): LayerOptions[] {
  return layers.map(layer => {
    switch (getLayerType(layer)) {
      case 'hover':
        return { ...layer, filter: hoveredFilter };
      case 'selected':
        return { ...layer, filter: selectedFilter };
      default:
        return layer;
    }
  });
}

function getLayerType(layer: LayerProps) {
  if (!!layer.id) return layer.id.split('/')[1];
  return '';
}
