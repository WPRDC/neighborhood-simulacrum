/**
 *
 * Indicator
 *
 */

import React from 'react';
import { useSelector } from 'react-redux';

import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { reducer, sliceKey } from './slice';
import { indicatorSaga } from './saga';
import { Indicator as IndicatorType } from '../../types';
import IndicatorCard from '../../components/IndicatorCard';
import { useHistory, useLocation } from 'react-router-dom';
import { IndicatorDetails } from '../../components/IndicatorDetails';
import { Heading, Item } from '@adobe/react-spectrum';
import { selectCurrentGeog } from '../Explorer/selectors';

interface Props {
  card?: boolean;
  indicator: IndicatorType;
}

export function Indicator(props: Props) {
  useInjectReducer({ key: sliceKey, reducer: reducer });
  useInjectSaga({ key: sliceKey, saga: indicatorSaga });

  const history = useHistory();
  const location = useLocation();

  const geog = useSelector(selectCurrentGeog);

  const { card, indicator } = props;
  const { domain, subdomain } = indicator.hierarchies[0];

  function handleExplore() {
    if (!!geog)
      history.push(
        `/${geog.geogType}/${geog.geogID}/${domain.slug}/${subdomain.slug}/${indicator.slug}`,
      );
  }

  function handleClose() {
    // remove indicator slug from end of url
    if (!!geog) history.push(`/${geog.geogType}/${geog.geogID}`);
  }

  function handleBreadcrumbClick(path: React.ReactText) {
    if (path === '__state' || typeof path !== 'string') {
      // fixme: '__state' check is hacky way of disabling first item
      return;
    }
    history.push(`/${path}`);
  }

  const breadCrumbsItems = [
    <Item key={domain.slug}>{domain.name}</Item>,
    <Item key={subdomain.slug}>{subdomain.name}</Item>,
    <Item key="__current">
      <Heading
        level={3}
        margin="size-100"
        marginTop-="size-0"
        UNSAFE_style={{ fontSize: '2rem' }}
      >
        {indicator.name}
      </Heading>
    </Item>,
  ];

  if (card)
    return <IndicatorCard indicator={indicator} onExplore={handleExplore} />;

  return (
    <IndicatorDetails
      indicator={indicator}
      breadCrumbItems={breadCrumbsItems}
      onBreadcrumbClick={handleBreadcrumbClick}
    />
  );
}
