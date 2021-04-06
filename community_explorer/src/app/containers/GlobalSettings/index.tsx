/**
 *
 * GlobalSettings
 *
 */

import React from 'react';
import { useSelector } from 'react-redux';

import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { reducer, sliceKey } from './slice';
import { selectColorMode } from './selectors';
import { globalSettingsSaga } from './saga';
import { defaultTheme, Provider } from '@adobe/react-spectrum';

interface Props extends React.PropsWithChildren<any> {}

export function GlobalSettings({ children }: Props) {
  useInjectReducer({ key: sliceKey, reducer: reducer });
  useInjectSaga({ key: sliceKey, saga: globalSettingsSaga });

  const colorScheme = useSelector(selectColorMode);

  return (
    <>
      <Provider theme={defaultTheme} colorScheme={colorScheme}>
        {children}
      </Provider>
    </>
  );
}
