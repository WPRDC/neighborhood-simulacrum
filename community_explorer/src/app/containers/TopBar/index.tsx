/**
 *
 * TopBar
 *
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector, useDispatch } from 'react-redux';

import { useInjectReducer } from 'utils/redux-injectors';
import { reducer, sliceKey } from './slice';
import { selectTopBar } from './selectors';
import { Heading, View } from '@adobe/react-spectrum';

interface Props {}



export function TopBar(props: Props) {
  useInjectReducer({ key: sliceKey, reducer: reducer });

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const topBar = useSelector(selectTopBar);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const dispatch = useDispatch();
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { t, i18n } = useTranslation();

  return (
    <View
      padding="size-150"
      height="size-1000"
      backgroundColor="gray-100"
      borderBottomWidth="thick"
    >
      <Heading level={1} alignSelf={'center'}>
        Child Health Data Explorer
      </Heading>
    </View>
  );
}
