/**
 *
 * TopBar
 *
 */

import React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { useInjectReducer } from 'utils/redux-injectors';
import { reducer, sliceKey } from './slice';

import { actions as globalSettingActions } from '../GlobalSettings/slice';
import {
  ActionButton,
  Button,
  DialogTrigger,
  Flex,
  Heading,
  View,
} from '@adobe/react-spectrum';

import Dark from '@spectrum-icons/workflow/Moon';
import Light from '@spectrum-icons/workflow/Light';
import { selectColorMode } from '../GlobalSettings/selectors';
import { ColorMode } from '../../types';
import { AboutDialog } from '../../components/AboutDialog';

interface Props {}

export function TopBar(props: Props) {
  useInjectReducer({ key: sliceKey, reducer: reducer });

  const colorMode = useSelector(selectColorMode);
  const dispatch = useDispatch();

  const ColorModeIcon = {
    [ColorMode.Dark]: Dark,
    [ColorMode.Light]: Light,
  }[colorMode];

  function handleColorModePress() {
    const newColorMode =
      colorMode === ColorMode.Dark ? ColorMode.Light : ColorMode.Dark;
    dispatch(globalSettingActions.changeColorMode(newColorMode));
  }

  return (
    <View
      padding="size-200"
      paddingTop="size-300"
      height="size-1000"
      backgroundColor="gray-100"
      borderBottomWidth="thick"
    >
      <Flex alignSelf="center" alignItems="center">
        <View flexGrow={1}>
          <Heading level={1} alignSelf={'center'} margin="size-0">
            Child Health Data Explorer
          </Heading>
        </View>
        <View paddingX="size-300">
          <DialogTrigger>
            <Button variant="primary">About</Button>
            {onClose => <AboutDialog onClose={onClose} />}
          </DialogTrigger>
        </View>
        <View>
          <ActionButton
            aria-label="toggle color theme"
            onPress={handleColorModePress}
          >
            <ColorModeIcon />
          </ActionButton>
        </View>
      </Flex>
    </View>
  );
}
