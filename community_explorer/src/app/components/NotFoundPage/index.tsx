import React from 'react';
import styled from 'styled-components/macro';
import { Helmet } from 'react-helmet-async';
import { Content, Heading, IllustratedMessage } from '@adobe/react-spectrum';
import NotFound from '@spectrum-icons/illustrations/NotFound';

export function NotFoundPage() {
  return (
    <>
      <Helmet>
        <title>404 Page Not Found</title>
        <meta name="description" content="Page not found" />
      </Helmet>
      <Wrapper>
        <IllustratedMessage>
          <NotFound />
          <Heading>Error 404: Page not found</Heading>
          <Content>
            This page isn't available. Try checking the URL or visit a different
            page.
          </Content>
        </IllustratedMessage>
      </Wrapper>
    </>
  );
}

const Wrapper = styled.div`
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  min-height: 320px;
`;

const Title = styled.div`
  margin-top: -8vh;
  font-weight: bold;
  color: black;
  font-size: 3.375rem;

  span {
    font-size: 3.125rem;
  }
`;
