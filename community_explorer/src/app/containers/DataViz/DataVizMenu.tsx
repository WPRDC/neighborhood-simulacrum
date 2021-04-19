import React from 'react';
import { Item, Menu, Text } from '@adobe/react-spectrum';
import { MenuItem } from './types';

interface Props {
  onMenuItemClick: (key: React.Key) => void;
  menuItems: MenuItem[];
}

export function DataVizMenu(props: Props) {
  const { onMenuItemClick, menuItems } = props;
  return (
    <Menu items={menuItems} onAction={onMenuItemClick}>
      {item => (
        <Item key={item.key}>
          {item.icon}
          <Text>{item.label}</Text>
        </Item>
      )}
    </Menu>
  );
}
