import { Described } from './common';
import { DataVizID } from './viz';

export * from './time';
export * from './variable';
export * from './viz';
export * from './source';

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

export interface Region extends Described, RegionBase {
  title: string;
  hierarchy: HierarchyItem[];
  resourcetype: string; // todo: make enums of the resourcetypes for use here.
  population: number;
  kidPopulation: number;
  regionType: RegionType;
  regionID: string;
}

export interface HierarchyItem {
  id: string | number;
  title: string;
  regionType: RegionType;
  regionID: string;
}

export interface RegionDescriptor {
  regionType: RegionType;
  regionID: string | number;
  name?: string;
}

export interface RegionBase {
  name: string;
  slug: string;
  description?: string;
}

// todo: define list of regiontypes
export type RegionType = string;

type URLNavParamKeys =
  | 'regionType'
  | 'regionID'
  | 'domainSlug'
  | 'subdomainSlug'
  | 'indicatorSlug';

export type URLNavParams = Record<URLNavParamKeys, string>;
