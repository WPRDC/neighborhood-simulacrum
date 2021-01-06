/**
 *
 * Explorer
 *
 */

import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useSelector, useDispatch } from 'react-redux';
import styled from 'styled-components/macro';

import { useParams, useHistory } from 'react-router-dom';

import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { actions, reducer, sliceKey } from './slice';
import {
  selectCurrentRegion,
  selectCurrentRegionIsLoading,
  // selectCurrentRegionLoadError,
  selectSelectedGeoLayer,
  // selectSelectedRegionID,
  selectTaxonomy,
  selectTaxonomyIsLoading,
  // selectTaxonomyLoadError,
} from './selectors';
import { explorerSaga } from './saga';

import { Grid } from '@react-spectrum/layout';
import { Text } from '@react-spectrum/text';
import { View } from '@react-spectrum/view';
import { NavMap } from '../../components/NavMap';
import { NavMenu } from '../../components/NavMenu';
import { RegionDashboard } from '../../components/RegionDashboard';
import { GeoLayer } from './types';
import { RegionDescriptor } from '../../types';

export function Explorer() {
  useInjectReducer({ key: sliceKey, reducer: reducer });
  useInjectSaga({ key: sliceKey, saga: explorerSaga });

  const dispatch = useDispatch();

  // routing
  const history = useHistory();
  const { regionType, regionID } = useParams();

  const taxonomy = useSelector(selectTaxonomy);
  const taxonomyIsLoading = useSelector(selectTaxonomyIsLoading);
  // const taxonomyLoadError = useSelector(selectTaxonomyLoadError);

  const currentRegion = useSelector(selectCurrentRegion);
  const currentRegionIsLoading = useSelector(selectCurrentRegionIsLoading);
  // const currentRegionLoadError = useSelector(selectCurrentRegionLoadError);

  const selectedGeoLayer = useSelector(selectSelectedGeoLayer);
  // const selectedRegionID = useSelector(selectSelectedRegionID);

  // init
  React.useEffect(() => {
    if (!taxonomy && !taxonomyIsLoading) {
      dispatch(actions.requestTaxonomy());
    }
  }, []);

  React.useEffect(() => {
    if (!!regionType && !!regionID) {
      handleRegionChange({ regionType, regionID });
    }
  }, [regionType, regionID]);

  function handleMapClick(regionDescriptor: RegionDescriptor) {
    history.push(
      `/${regionDescriptor.regionType}/${regionDescriptor.regionID}`,
    );
  }

  function handleRegionChange(regionDescriptor: RegionDescriptor) {
    dispatch(actions.selectRegion(regionDescriptor));
    dispatch(actions.requestRegionDetails(regionDescriptor));
  }

  function handleSelectGeoLayer(geoLayer: GeoLayer) {
    dispatch(actions.selectGeoLayer(geoLayer));
  }

  return (
    <>
      <Helmet>
        <title>Child Health Data Explorer</title>
        <meta name="description" content="Data explorer" />
      </Helmet>
      <Grid
        areas={['sidebar  content', 'map content']}
        columns={['3fr', '5fr']}
        rows={['1fr', '2fr']}
        flex
        minHeight="0px"
      >
        <View gridArea="map" borderTopWidth="thicker">
          <NavMap menuLayer={selectedGeoLayer} onClick={handleMapClick} />
        </View>

        <View gridArea="sidebar">
          <NavMenu
            handleLayerSelect={handleSelectGeoLayer}
            selectedGeoLayer={selectedGeoLayer}
          />
        </View>

        <View gridArea="content" overflow="auto" borderStartWidth="thicker">
          {!!taxonomy && (
            <RegionDashboard
              taxonomy={taxonomy}
              taxonomyIsLoading={taxonomyIsLoading}
              region={currentRegion}
              regionIsLoading={currentRegionIsLoading}
            />
          )}
        </View>
      </Grid>

      <Div>
        <Text>&copy; 2021 Western Pennsylvania Regional Data Center</Text>
      </Div>
    </>
  );
}

const Div = styled.div``;
