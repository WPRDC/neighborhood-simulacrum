import React from 'react';
import styled from 'styled-components';
import { Text, View } from '@adobe/react-spectrum';
import { components, OptionProps } from 'react-select';

interface Props extends OptionProps<any> {
  data: Record<'name' | 'description', string>;
}

export function Option(props: Props) {
  const { innerProps, data } = props;
  const { name, description } = data;
  return (
    <OptionWrapper {...innerProps} {...props}>
      <View>
        <View>
          <Text UNSAFE_style={{ fontWeight: 'bold' }}>{name}</Text>
        </View>
        <View>
          <Text>{description} </Text>
        </View>
      </View>
    </OptionWrapper>
  );
}

const OptionWrapper = styled(components.Option)`
  background-color: ${({ isDisabled, isSelected, isFocused }) => {
    if (isDisabled) return null;
    if (isFocused) return '#ddd !important';
    if (isSelected) return '#bebebe !important';

    return 'default';
  }};

  &:not(:last-child) {
    padding-bottom: 4px;
    border-bottom: 1px solid #cecece;
  }
`;
