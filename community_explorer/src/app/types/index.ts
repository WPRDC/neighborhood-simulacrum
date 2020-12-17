import { Described } from './common';
import { DataVizID } from './viz';

export * from './time';
export * from './variable';
export * from './viz';

export interface Indicator extends Described {
  dataVizes: DataVizID[];
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
}

interface HierarchyItem {
  id: string | number;
  title: string;
}

export interface RegionID {
  regionType: string; // todo: define list of regiontypes
  geoid: string | number;
  name?: string;
}

export interface RegionBase {
  name: string;
  slug: string;
  description?: string;
}
