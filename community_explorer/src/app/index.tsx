/**
 *
 * App
 *
 * This component is the skeleton around the actual pages, and should only
 * contain code that should be seen on all pages. (e.g. navigation bar)
 */

import * as React from 'react';
import { Switch, Route, BrowserRouter } from 'react-router-dom';

import { GlobalStyle } from 'styles/global-styles';

import { NotFoundPage } from './components/NotFoundPage/Loadable';

import { Flex } from '@react-spectrum/layout';
import { Provider } from '@react-spectrum/provider';
import { theme as defaultTheme } from '@react-spectrum/theme-default';

import { TopBar } from './containers/TopBar';
import { Explorer } from './containers/Explorer';

import 'mapbox-gl/dist/mapbox-gl.css';

export function App() {
  return (
    <Provider theme={defaultTheme} colorScheme="light">
      <BrowserRouter>
        <Flex height="100vh" direction="column">
          <TopBar />
          <Switch>
            <Route path="/:regionType?/:regionID?">
              <Explorer />
            </Route>
            <Route component={NotFoundPage} />
          </Switch>
        </Flex>
        <GlobalStyle />
      </BrowserRouter>
    </Provider>
  );
}
