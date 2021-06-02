/**
 *
 * NavMap
 *
 */
import React from 'react';
import { GeogTypeDescriptor } from '../../containers/Explorer/types';

import {
  fetchCartoVectorSource,
  LayerOptions,
  Map,
  SimpleLabelPopupContent,
} from 'wprdc-components';
import { SourceProps } from 'react-map-gl';

import menuLayers from './menuLayers';
import { MAPBOX_API_TOKEN } from '../../settings';
import { ColorMode, GeogIdentifier } from '../../types';
import { censusFilter } from './settings';
import layerSpec, { makeLayers } from './layerSpec';

interface Props {
  selectedGeoLayer?: GeogTypeDescriptor;
  selectedGeog?: GeogIdentifier;
  onClick: (selection: {
    geogType: string;
    geogID: string;
    name: string;
  }) => void;
  colorScheme: ColorMode;
}

export function NavMap(props: Props) {
  const { selectedGeoLayer, selectedGeog, onClick, colorScheme } = props;
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
    if (selectedGeoLayer) {
      const { source, layers } = makeMapData(selectedGeoLayer);
      setMbLayers(layers as LayerOptions[]);
      setMbSource(undefined);
      setInteractiveLayerIds(
        layers
          .filter(layerFilter)
          .filter(l => !!l.id)
          .map(l => l.id),
      );

      fetchCartoVectorSource(
        selectedGeoLayer.id,
        source.sql,
        // eslint-disable-next-line no-console
      ).then(receiveMbSource, err => console.warn('CARTO', err));
    }
  }, [selectedGeoLayer]);

  React.useEffect(() => {
    if (!!selectedGeog)
      setSelectedFilter(filterLayerByGeogID(selectedGeog.geogID));
  }, [selectedGeog]);

  function receiveMbSource(sourceData) {
    setMbSource(sourceData);
  }

  function handleHover(e) {
    if (e.features.length) {
      const { geogid: geogID } = e.features[0].properties;
      setHoveredFilter(filterLayerByGeogID(geogID));
    } else {
      setHoveredFilter(clearLayerFilter());
    }
  }

  function handleClick(e) {
    if (e && e.features && e.features.length) {
      const {
        geogtype: geogType,
        geogid: geogID,
        name,
      } = e.features[0].properties;
      setSelectedFilter(filterLayerByGeogID(geogID));
      onClick({ geogType, geogID, name });
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
      hoverPopupContent={SimpleLabelPopupContent}
      defaultViewport={{ zoom: 8, longitude: -79.9925 }}
      interactiveLayerIds={mbSource ? interactiveLayerIds : []}
      onHover={handleHover}
      onClick={handleClick}
      mapboxApiAccessToken={MAPBOX_API_TOKEN}
      sources={mapSources}
      layers={mapLayers}
      basemapStyle={colorScheme}
    />
  );
}

const layerType = l => l.id.split('/')[1];

const layerFilter = l => layerType(l) === 'fill';

function filterLayerByGeogID(geogID: string) {
  return ['==', 'geogid', geogID];
}

function clearLayerFilter() {
  return ['==', 'geogid', 'w00t'];
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

function getLayerType(layer: LayerOptions) {
  if (!!layer.id) return layer.id.split('/')[1];
  return '';
}

function makeMapData(selectedGeoLayer: GeogTypeDescriptor) {
  const source = {
    type: 'vector',
    minzoom: 0,
    maxzoom: 11,
    source: selectedGeoLayer.tableName,
    sql: selectedGeoLayer.cartoSql,
  };
  const layers = makeLayers(selectedGeoLayer.id);

  return { source, layers };
}
