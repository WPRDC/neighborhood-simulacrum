/**
 *
 * RegionDashboard
 *
 */
import React from 'react';
import styled from 'styled-components/macro';
import { Heading } from '@react-spectrum/text';
import { ProgressBar, ProgressCircle } from '@react-spectrum/progress';
import { Content, View } from '@react-spectrum/view';
import { Tabs } from '@react-spectrum/tabs';
import { Breadcrumbs } from 'wprdc-components';
import { Item } from '@react-stately/collections';
import SubdomainSection from './SubdomainSection';
import { Region, Taxonomy } from '../../types';
import { Flex } from '@react-spectrum/layout';

interface Props {
  taxonomy: Taxonomy;
  taxonomyIsLoading: boolean;
  region?: Region;
  regionIsLoading: boolean;
}

export function RegionDashboard(props: Props) {
  const { taxonomy, taxonomyIsLoading, region, regionIsLoading } = props;
  const [currentTab, setCurrentTab] = React.useState<string>();

  const handleTabChange = (newValue: React.ReactText) => {
    setCurrentTab(newValue as string);
  };

  if (taxonomyIsLoading) {
    return (
      <Wrapper>
        <Heading level={1}>Gathering data...</Heading>
      </Wrapper>
    );
  }

  const breadCrumbItems =
    region && region.hierarchy.map(h => ({ ...h, label: h.title }));

  return (
    <Wrapper>
      <View paddingX="size-100">
        {regionIsLoading && (
          <ProgressCircle
            isIndeterminate
            aria-label="Loading region details"
            size="S"
            position="absolute"
            top="size-100"
            left="size-100"
          />
        )}
        <Heading level={1}>{!!region ? region.title : 'Loading...'}</Heading>

        {/*{!!region && <Breadcrumbs items={breadCrumbItems} />}*/}
      </View>
      <Tabs
        onSelectionChange={handleTabChange}
        selectedKey={currentTab}
        defaultSelectedKey={taxonomy[0].slug}
      >
        {taxonomy.map(domain => (
          <Item title={domain.name} key={domain.slug}>
            <Content margin="size-100">
              {domain.subdomains.map(subdomain => (
                <SubdomainSection key={subdomain.slug} subdomain={subdomain} />
              ))}
            </Content>
          </Item>
        ))}
      </Tabs>
    </Wrapper>
  );
}

const Wrapper = styled.div`
  width: 100%;
  min-height: 100%;
  max-height: 100%;
  overflow: auto;
  top: 0;
  display: -webkit-flex;
  display: -ms-flex;
  display: flex;
  -webkit-flex-direction: column;
  -ms-flex-direction: column;
  flex-direction: column;
  position: relative;
`;
