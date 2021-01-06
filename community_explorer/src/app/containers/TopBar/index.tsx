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
import { View } from '@react-spectrum/view';
import { Heading } from '@react-spectrum/text';
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
      height="size-1250"
      backgroundColor="static-blue-200"
      borderBottomWidth="thick"
    >
      <Heading level={1} alignSelf={'center'}>
        Child Health Data Explorer
      </Heading>
    </View>
  );
}
