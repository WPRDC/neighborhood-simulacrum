/**
 *
 * Sentence
 *
 */
import React from 'react';
// import styled from 'styled-components/macro';
import { View, Text } from '@adobe/react-spectrum';
import { SentenceData } from '../../types';

interface Props {
  text: string;
  data: SentenceData;
}

function parseSentence(sentence): string {
  const doc = new DOMParser().parseFromString(sentence, 'text/html');
  if (doc.documentElement.textContent) return doc.documentElement.textContent;
  return '';
}

export function Sentence(props: Props) {
  const { data } = props;
  const cleanSentence = parseSentence(data);
  return (
    <View>
      <Text>
        <span dangerouslySetInnerHTML={{ __html: cleanSentence }} />
      </Text>
    </View>
  );
}
