import { Described } from './common';
import { DataVizID } from './viz';

export * from './time';
export * from './variable';
export * from './viz';
export * from './source';
export * from './geog';

export enum IndicatorLayout {
  A = 'A',
  B = 'B',
  C = 'C',
  D = 'D',
}

interface IndicatorHierarchy {
  domain: Described;
  subdomain: Described;
}

export interface Indicator extends Described {
  longDescription: string;
  limitations: string;
  importance: string;
  source: string;
  provenance: string;
  layout: IndicatorLayout;
  dataVizes: DataVizID[];
  hierarchies: IndicatorHierarchy[];
}

export interface Subdomain extends Described {
  indicators: Indicator[];
}

export interface Domain extends Described {
  subdomains: Subdomain[];
}

export type Taxonomy = Domain[];

export interface Geog extends Described, GeogBase {
  title: string;
  hierarchy: GeogDescriptor[];
  resourcetype: string; // todo: make enums of the resourcetypes for use here.
  population: number;
  kidPopulation: number;
  geogType: GeogType;
  geogID: string;
}

export interface GeogDescriptor extends GeogIdentifier {
  id: string | number;
  title: string;
}

export interface GeogIdentifier {
  id?: string | number;
  geogType: GeogType;
  geogID: string;
}

export interface GeogBase {
  name: string;
  slug: string;
  description?: string;
}

// todo: define list of geogtypes
export type GeogType = string;

type URLNavParamKeys =
  | 'geogType'
  | 'geogID'
  | 'domainSlug'
  | 'subdomainSlug'
  | 'indicatorSlug';

export type URLNavParams = Record<URLNavParamKeys, string>;

export enum ColorMode {
  Light = 'light',
  Dark = 'dark',
}
