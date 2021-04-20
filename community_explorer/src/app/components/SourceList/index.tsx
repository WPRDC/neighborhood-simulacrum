/**
 *
 * SourceList
 *
 */
import React from 'react';
import { ActionButton, DialogTrigger, Flex, View } from '@adobe/react-spectrum';
import { Text } from '@react-spectrum/text';
import { ColorMode, SourceBase } from '../../types';
import styled from 'styled-components/macro';
import { SourceDialog } from '../SourceDialog';

interface Props {
  sources: SourceBase[];
  colorScheme: ColorMode;
}

export function SourceList(props: Props) {
  const { sources } = props;
  return (
    <View>
      <Flex alignItems="center">
        <View>
          <Text marginBottom={0}>
            <Strong>Source{sources.length > 1 ? 's' : ''}:</Strong>
          </Text>
        </View>
        <View>
          <Ul>
            {sources.map(source => (
              <Li>
                <DialogTrigger type="popover">
                  <ActionButton
                    marginY={0}
                    isQuiet
                    UNSAFE_style={{ cursor: 'pointer' }}
                  >
                    <ButtonText>{source.name}</ButtonText>
                  </ActionButton>
                  {onClose => (
                    <SourceDialog onClose={onClose} source={source} />
                  )}
                </DialogTrigger>
              </Li>
            ))}
          </Ul>
        </View>
      </Flex>
    </View>
  );
}

const ButtonText = styled.span`
  color: var(--spectrum-global-color-gray-800);
  font-style: italic;
  text-decoration: underline;
`;

const Strong = styled.strong`
  font-weight: 600;
`;

const Ul = styled.ul`
  list-style: none;
  display: inline-block;
  padding-left: 0;
  margin-bottom: 0;
  margin-top: 0;
`;

const Li = styled.li`
  padding-left: 8px;
  display: inline-block;
  font-style: italic;
  color: var(--spectrum-global-color-gray-800);
`;

const A = styled.a`
  color: var(--spectrum-global-color-gray-800);
`;
