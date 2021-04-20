/**
 *
 * Explorer
 *
 */

import React from 'react';
import { Helmet } from 'react-helmet-async';
import { useDispatch, useSelector } from 'react-redux';

import { useHistory, useParams } from 'react-router-dom';

import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { actions, reducer, sliceKey } from './slice';
import {
  selectCurrentGeog,
  selectCurrentGeogIsLoading,
  selectGeogsListRecord,
  selectGeogsListsAreLoadingRecord,
  selectSelectedGeogIdentifier,
  selectSelectedGeoLayer,
  selectTaxonomy,
  selectTaxonomyIsLoading,
} from './selectors';
import { explorerSaga } from './saga';

import { NavMap } from '../../components/NavMap';
import { NavMenu } from '../../components/NavMenu';
import { GeogTypeDescriptor } from './types';
import { GeogIdentifier, URLNavParams } from '../../types';
import { GeographySection } from '../../components/GeographySection';
import { TaxonomySection } from '../../components/TaxonomySection';
import { Grid, Text, View } from '@adobe/react-spectrum';
import { selectColorMode } from '../GlobalSettings/selectors';
import { Link } from 'wprdc-components';
import { DEFAULT_GEOG_TYPE } from '../../settings';
import { getDescriptorForGeogType } from '../../util';

export function Explorer() {
  useInjectReducer({ key: sliceKey, reducer: reducer });
  useInjectSaga({ key: sliceKey, saga: explorerSaga });

  const dispatch = useDispatch();

  // routing
  const history = useHistory();
  const {
    geogType,
    geogID,
    domainSlug,
    subdomainSlug,
    indicatorSlug,
    dataVizSlug,
  } = useParams<URLNavParams>();

  const taxonomy = useSelector(selectTaxonomy);
  const taxonomyIsLoading = useSelector(selectTaxonomyIsLoading);
  // const taxonomyLoadError = useSelector(selectTaxonomyLoadError);

  const currentGeog = useSelector(selectCurrentGeog);
  const currentGeogIsLoading = useSelector(selectCurrentGeogIsLoading);
  // const currentGeogLoadError = useSelector(selectCurrentGeogLoadError);

  const selectedGeoLayer = useSelector(selectSelectedGeoLayer);
  const selectedGeog = useSelector(selectSelectedGeogIdentifier);

  const colorScheme = useSelector(selectColorMode);

  const geogsListsRecord = useSelector(selectGeogsListRecord);
  const geogsListsAreLoadingRecord = useSelector(
    selectGeogsListsAreLoadingRecord,
  );

  // init
  React.useEffect(() => {
    dispatch(
      actions.selectGeoType(
        getDescriptorForGeogType(geogType) || DEFAULT_GEOG_TYPE,
      ),
    );
    if (!taxonomy && !taxonomyIsLoading) {
      dispatch(actions.requestTaxonomy());
    }
    if (!geogType || !geogID) {
      history.push('/countySubdivision/4200361000');
    }
  }, []);

  // switch geog on url change
  React.useEffect(() => {
    if (!!geogType && !!geogID) {
      handleGeogChange({ geogType: geogType, geogID: geogID });
    }
  }, [geogType, geogID]);

  function handleMapClick(geogIdentifier: GeogIdentifier) {
    const domainPath = domainSlug ? `/${domainSlug}` : '';
    const subdomainPath = subdomainSlug ? `/${subdomainSlug}` : '';
    const indicatorPath = indicatorSlug ? `/${indicatorSlug}` : '';
    const dataVizPath = dataVizSlug ? `/${dataVizSlug}` : '';
    const extraPath = `${domainPath}${subdomainPath}${indicatorPath}${dataVizPath}`;
    history.push(
      `/${geogIdentifier.geogType}/${geogIdentifier.geogID}${extraPath}`,
    );
  }

  function handleGeogChange(geogIdentifier: GeogIdentifier) {
    dispatch(actions.selectGeog(geogIdentifier));
    dispatch(actions.requestGeogDetails(geogIdentifier));
  }

  function handleSelectGeoLayer(geoLayer: GeogTypeDescriptor) {
    dispatch(actions.selectGeoType(geoLayer));
  }

  return (
    <>
      <Helmet>
        <title>Child Health Data Explorer</title>
        <meta name="description" content="Data explorer" />
      </Helmet>
      <Grid
        areas={['sidebar  content', 'map content']}
        columns={['2fr', '5fr']}
        rows={['1fr', '2fr']}
        flex
        minHeight="0px"
      >
        <View gridArea="map" borderTopWidth="thicker">
          <NavMap
            selectedGeoLayer={selectedGeoLayer}
            onClick={handleMapClick}
            colorScheme={colorScheme}
            selectedGeog={selectedGeog}

          />
        </View>

        <View gridArea="sidebar">
          <NavMenu
            onLayerSelect={handleSelectGeoLayer}
            onGeogSelect={handleGeogChange}
            selectedGeoLayer={selectedGeoLayer}
            selectedGeog={selectedGeog}
            geogsListsRecord={geogsListsRecord}
            geogsListsAreLoadingRecord={geogsListsAreLoadingRecord}
          />
        </View>

        <View
          gridArea="content"
          overflow="auto"
          borderStartWidth="thicker"
          backgroundColor="gray-300"
        >
          <GeographySection
            geog={currentGeog}
            geogIsLoading={currentGeogIsLoading}
          />
          <TaxonomySection
            taxonomy={taxonomy}
            taxonomyIsLoading={taxonomyIsLoading}
            currentGeog={currentGeog}
            currentDomainSlug={domainSlug}
            currentSubdomainSlug={subdomainSlug}
            currentIndicatorSlug={indicatorSlug}
            currentDataVizSlug={dataVizSlug}
          />
        </View>
      </Grid>

      <View padding="size-50">
        <Text>
          <Link>
            <a href="https://www.wprdc.org">
              Western Pennsylvania Regional Data Center
            </a>
          </Link>
        </Text>
      </View>
    </>
  );
}
