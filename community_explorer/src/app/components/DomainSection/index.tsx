/**
 *
 * DomainSection
 *
 */
import React from 'react';
import { Heading, Text, View } from '@adobe/react-spectrum';
import { Domain } from 'app/types';
import { SubdomainSection } from '../SubdomainSection';

interface Props {
  domain: Domain;
  currentSubdomainSlug?: string;
}

export function DomainSection({ domain }: Props) {
  return (
    <View>
      <Heading level={3}>{domain.name}</Heading>
      <Text>{domain.description}</Text>
      {domain.subdomains.map(subdomain => (
        <SubdomainSection key={subdomain.slug} subdomain={subdomain} />
      ))}
    </View>
  );
}
