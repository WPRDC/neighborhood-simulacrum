/**
 *
 * App
 *
 * This component is the skeleton around the actual pages, and should only
 * contain code that should be seen on all pages. (e.g. navigation bar)
 */

import * as React from 'react';
import { Switch, Route, BrowserRouter } from 'react-router-dom';

import { NotFoundPage } from './components/NotFoundPage/Loadable';

import { Flex, Provider, defaultTheme } from '@adobe/react-spectrum';

import { TopBar } from './containers/TopBar';
import { Explorer } from './containers/Explorer';

import 'mapbox-gl/dist/mapbox-gl.css';

export function App() {
  return (
    <Provider theme={defaultTheme}>
      <BrowserRouter>
        <Flex height="100vh" direction="column">
          <TopBar />
          <Switch>
            <Route path="/:regionType?/:regionID?/:domainSlug?/:subdomainSlug?/:indicatorSlug?">
              <Explorer />
            </Route>
            <Route component={NotFoundPage} />
          </Switch>
        </Flex>
      </BrowserRouter>
    </Provider>
  );
}
