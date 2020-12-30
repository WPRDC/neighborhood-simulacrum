/**
 *
 * RegionDashboard
 *
 */
import React from 'react';
import styled from 'styled-components/macro';
import { Heading } from '@react-spectrum/text';
import { ProgressCircle } from '@react-spectrum/progress';
import { Content, View } from '@react-spectrum/view';
import { Tabs } from '@react-spectrum/tabs';
import { Breadcrumbs } from 'wprdc-components';
import { Item } from '@react-spectrum/breadcrumbs';
import SubdomainSection from './SubdomainSection';
import { Region, Taxonomy } from '../../types';
import { useHistory } from 'react-router-dom';

interface Props {
  taxonomy: Taxonomy;
  taxonomyIsLoading: boolean;
  region?: Region;
  regionIsLoading: boolean;
}

export function RegionDashboard(props: Props) {
  const { taxonomy, taxonomyIsLoading, region, regionIsLoading } = props;
  const [currentTab, setCurrentTab] = React.useState<string>();

  const history = useHistory();

  const handleTabChange = (newValue: React.ReactText) => {
    setCurrentTab(newValue as string);
  };

  function handleBreadcrumbClick(path: React.ReactText) {
    if (path === '__state' || typeof path !== 'string') {
      // fixme: '__state' check is hacky way of disabling first item
      return;
    }
    history.push(`/${path}`);
  }

  const showAbout = !region && !regionIsLoading;
  if (showAbout) {
    return (
      <Wrapper>
        <About />
      </Wrapper>
    );
  }

  if (taxonomyIsLoading) {
    return (
      <Wrapper>
        <Heading level={1}>Gathering data...</Heading>
      </Wrapper>
    );
  }

  const breadCrumbItems = region && [
    <Item key="__state">Pennsylvania</Item>,
    ...region.hierarchy.map(h => (
      <Item key={`${h.regionType}/${h.regionID}`}>{h.title}</Item>
    )),
    <Item key="__current">
      <Heading level={1} margin="size-100" marginTop-="size-0">
        {region.title}
      </Heading>
    </Item>,
  ];

  return (
    <Wrapper>
      <View>
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

        {!!region ? (
          <Breadcrumbs isMultiline size="L" onAction={handleBreadcrumbClick}>
            {breadCrumbItems}
          </Breadcrumbs>
        ) : (
          <Heading level={2} marginStart="size-100">
            Loading...
          </Heading>
        )}
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

const About = () => (
  <View padding="size-150">
    <Heading level={2}>Welcome to this thing.</Heading>
    <p>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quisque interdum
      ligula at rutrum ultrices. Aenean in leo non leo fermentum varius eu ac
      risus. Cras vulputate dolor tempor felis iaculis finibus. Nam tincidunt ex
      in tincidunt blandit. Praesent consequat nunc facilisis accumsan accumsan.
      Duis odio sem, mattis eu nibh at, ornare faucibus diam. Vivamus suscipit
      cursus velit, vitae mollis mi sodales nec. Nam malesuada lacus sit amet
      tortor porta vulputate.
    </p>

    <p>
      Etiam at tellus vel mi vehicula molestie. Donec auctor nisl erat, eget
      maximus arcu consectetur a. Quisque justo tellus, imperdiet posuere nisi
      ut, ultricies tristique velit. Duis aliquam in risus mattis ultricies. Sed
      rhoncus condimentum orci rutrum bibendum. Fusce mauris odio, fringilla at
      sollicitudin ac, blandit nec orci. Donec nec suscipit turpis, ac malesuada
      ante. Vivamus sagittis tincidunt scelerisque. Fusce sollicitudin lacinia
      blandit. Orci varius natoque penatibus et magnis dis parturient montes,
      nascetur ridiculus mus. Morbi vitae elit magna.
    </p>

    <p>
      Phasellus erat orci, cursus eu ex maximus, convallis efficitur odio. Ut
      vestibulum at nulla eu hendrerit. Etiam id rhoncus dui. Nullam eget magna
      ex. In elementum tortor ac mattis aliquam. Sed lacinia dui diam, sit amet
      malesuada tortor varius imperdiet. Sed aliquam tortor ut tellus
      ullamcorper commodo. Integer sagittis aliquam elit. In vitae velit rutrum,
      cursus lectus a, venenatis sem. Nunc in enim quis lacus vehicula lobortis
      sed eget turpis. Cras metus turpis, cursus quis augue quis, blandit
      condimentum eros. Aliquam et nibh sed nulla fermentum mollis vel vel
      felis.
    </p>

    <p>
      Praesent scelerisque scelerisque dolor sed tempus. Praesent ac velit at mi
      elementum fringilla vitae eget ante. Phasellus tempor aliquam odio, sit
      amet semper ante fermentum at. Duis ac velit eget metus consectetur
      posuere in et leo. Integer sit amet efficitur leo. Aenean id ipsum enim.
      Cras mollis malesuada leo vel mattis. Suspendisse potenti. Etiam efficitur
      facilisis mi ac vulputate. Nunc placerat consectetur neque ut feugiat.
      Duis vitae varius neque, vel semper arcu.
    </p>

    <p>
      Vivamus id libero pellentesque odio mattis sagittis a a leo. Pellentesque
      lacus turpis, faucibus in pulvinar id, pellentesque a sapien. Quisque
      tellus tellus, cursus ut ex nec, ullamcorper rutrum augue. Donec eget est
      rutrum, ullamcorper nisl vel, tincidunt massa. Etiam nec porta est. Sed
      aliquet placerat porttitor. Praesent rhoncus est vel ipsum sagittis, eu
      ullamcorper purus fringilla. Curabitur in sodales ex. Pellentesque
      accumsan aliquet ornare. Cras id massa vel diam malesuada consectetur.
      Aliquam commodo eu ligula eu posuere. Curabitur eget vestibulum metus.
      Aenean nec volutpat ligula. Vestibulum nisl nunc, efficitur nec fermentum
      at, feugiat ac sem.
    </p>
  </View>
);

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
