/**
 *
 * Sentence
 *
 */
import React from 'react';
// import styled from 'styled-components/macro';
import { Text, View } from '@adobe/react-spectrum';
import { SentenceViz, TabularData, VizProps } from '../../types';

interface Props extends VizProps<SentenceViz, TabularData> {}

export const Sentence = (props: Props) => {
  const { dataViz } = props;
  // const cleanSentence = parseSentence(dataViz.data);
  return (
    <View>
      <Text>
        <span>🚧</span> Coming back soon...
      </Text>
    </View>
  );
};

// function parseSentence(sentence): string {
//   const doc = new DOMParser().parseFromString(sentence, 'text/html');
//   if (doc.documentElement.textContent) return doc.documentElement.textContent;
//   return '';
// }
