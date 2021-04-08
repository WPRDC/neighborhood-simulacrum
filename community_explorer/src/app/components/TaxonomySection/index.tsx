/**
 *
 * TaxonomySection
 *
 */
import React from 'react';
import { Geog, Taxonomy } from '../../types';
import { DomainSection } from '../DomainSection';

import { Content, Item, Text } from '@adobe/react-spectrum';
import { Tabs } from '@react-spectrum/tabs';
import { useHistory } from 'react-router-dom';
import { Indicator } from '../../containers/Indicator';

interface Props {
  taxonomy?: Taxonomy;
  taxonomyIsLoading: boolean;
  currentGeog?: Geog;
  currentDomainSlug?: string;
  currentSubdomainSlug?: string;
  currentIndicatorSlug?: string;
}

export function TaxonomySection(props: Props) {
  const {
    taxonomy,
    taxonomyIsLoading,
    currentGeog,
    currentDomainSlug,
    currentSubdomainSlug,
    currentIndicatorSlug,
  } = props;
  //todo: make this a container?
  const history = useHistory();

  const handleTabChange = (newValue: React.ReactText) => {
    if (!!currentGeog)
      history.push(
        `/${currentGeog.geogType}/${currentGeog.geogID}/${newValue}`,
      );
  };

  if (taxonomyIsLoading) {
    return <Text>Gathering data...</Text>;
  }

  const currentIndicator = getIndicator(taxonomy, currentIndicatorSlug);

  if (taxonomy) {
    return (
      <Tabs
        onSelectionChange={handleTabChange}
        selectedKey={currentDomainSlug}
        defaultSelectedKey={taxonomy[0].slug}
      >
        {taxonomy.map(domain => (
          <Item title={domain.name} key={domain.slug}>
            <Content margin="size-200">
              {currentIndicator ? (
                <Indicator indicator={currentIndicator} />
              ) : (
                <DomainSection
                  domain={domain}
                  currentSubdomainSlug={currentSubdomainSlug}
                />
              )}
            </Content>
          </Item>
        ))}
      </Tabs>
    );
  }
  return <div />;
}

function getIndicator(taxonomy?: Taxonomy, slug?: string) {
  if (taxonomy && slug) {
    for (let domain of taxonomy) {
      for (let subdomain of domain.subdomains) {
        for (let indicator of subdomain.indicators) {
          if (indicator.slug === slug) return indicator;
        }
      }
    }
  }
  return null;
}
