/**
 *
 * Sentence
 *
 */
import React from 'react';
// import styled from 'styled-components/macro';
import { Text, View } from '@adobe/react-spectrum';
import { SentenceData, SentenceViz, VizProps } from '../../types';

interface Props extends VizProps<SentenceViz, SentenceData> {}

export const Sentence = (props: Props) => {
  const { dataViz } = props;
  const cleanSentence = parseSentence(dataViz.data);
  return (
    <View>
      <Text>
        <span dangerouslySetInnerHTML={{ __html: cleanSentence }} />
      </Text>
    </View>
  );
};

function parseSentence(sentence): string {
  const doc = new DOMParser().parseFromString(sentence, 'text/html');
  if (doc.documentElement.textContent) return doc.documentElement.textContent;
  return '';
}
