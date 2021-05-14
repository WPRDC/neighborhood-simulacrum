/**
 *
 * TaxonomySection
 *
 */
import React from 'react';
import { DataVizID, Geog, Indicator, Taxonomy } from '../../types';
import { DomainSection } from '../DomainSection';

import { View, Item, Text } from '@adobe/react-spectrum';
import { TabList, TabPanels, Tabs } from '@react-spectrum/tabs';
import { useHistory } from 'react-router-dom';
import { Indicator as IndicatorContainer } from '../../containers/Indicator';
import { DataViz as DataVizContainer } from '../../containers/DataViz';
import { DataVizVariant } from '../../containers/DataViz/types';

interface Props {
  taxonomy?: Taxonomy;
  taxonomyIsLoading: boolean;
  currentGeog?: Geog;
  currentDomainSlug?: string;
  currentSubdomainSlug?: string;
  currentIndicatorSlug?: string;
  currentDataVizSlug?: string;
}

export function TaxonomySection(props: Props) {
  const {
    taxonomy,
    taxonomyIsLoading,
    currentGeog,
    currentDomainSlug,
    currentSubdomainSlug,
    currentIndicatorSlug,
    currentDataVizSlug,
  } = props;
  //todo: make this a container?
  const history = useHistory();
  const content = React.useMemo(
    () => getContent(taxonomy, currentIndicatorSlug, currentDataVizSlug),
    [taxonomy, currentIndicatorSlug, currentDataVizSlug],
  );
  const handleTabChange = (newValue: React.ReactText) => {
    if (!!currentGeog)
      history.push(
        `/${currentGeog.geogType}/${currentGeog.geogID}/${newValue}`,
      );
  };

  if (taxonomyIsLoading) {
    return <Text margin="size-200">Gathering data...</Text>;
  }
  if (taxonomy) {
    return (
      <Tabs
        aria-label="primary categories"
        onSelectionChange={handleTabChange}
        selectedKey={currentDomainSlug}
        defaultSelectedKey={taxonomy[0].slug}
      >
        <View paddingX="size-200">
          <TabList>
            {taxonomy.map(domain => (
              <Item key={domain.slug}>{domain.name}</Item>
            ))}
          </TabList>
          <TabPanels>
            {taxonomy.map(domain => (
              <Item key={domain.slug}>
                {!!content ? (
                  content
                ) : (
                  <DomainSection
                    domain={domain}
                    currentSubdomainSlug={currentSubdomainSlug}
                  />
                )}
              </Item>
            ))}
          </TabPanels>
        </View>
      </Tabs>
    );
  }
  console.warn('No taxonomy found.');
  return <div />;
}

/**
 * Search through taxonomy to find indicator with slug `slug`
 * @param taxonomy
 * @param slug
 */
function getIndicator(
  taxonomy?: Taxonomy,
  slug?: string,
): Indicator | undefined {
  if (taxonomy && slug) {
    for (let domain of taxonomy) {
      for (let subdomain of domain.subdomains) {
        for (let indicator of subdomain.indicators) {
          if (indicator.slug === slug) return indicator;
        }
      }
    }
  }
  return undefined;
}

/**
 * Find indicator in taxonomy.
 * @param taxonomy
 * @param indicatorSlug
 * @param dataVizSlug
 */
function getDataViz(
  taxonomy?: Taxonomy,
  indicatorSlug?: string,
  dataVizSlug?: string,
): DataVizID | undefined {
  if (taxonomy && indicatorSlug && dataVizSlug) {
    const indicator = getIndicator(taxonomy, indicatorSlug);
    return !!indicator
      ? indicator.dataVizes.find(dv => dv.slug === dataVizSlug)
      : undefined;
  }
  return undefined;
}

/**
 * Get content based on what path data is available
 * @param taxonomy
 * @param indicatorSlug
 * @param dataVizSlug
 */
function getContent(taxonomy, indicatorSlug, dataVizSlug) {
  if (dataVizSlug && indicatorSlug) {
    const currentDataViz = getDataViz(taxonomy, indicatorSlug, dataVizSlug);
    return currentDataViz ? (
      <DataVizContainer
        dataVizID={currentDataViz}
        variant={DataVizVariant.Details}
        taxonomy={taxonomy}
      />
    ) : undefined;
  } else if (indicatorSlug) {
    const currentIndicator = getIndicator(taxonomy, indicatorSlug);
    return currentIndicator ? (
      <IndicatorContainer indicator={currentIndicator} />
    ) : undefined;
  }
}
