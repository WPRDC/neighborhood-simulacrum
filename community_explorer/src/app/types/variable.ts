/*
 *
 * Variable types
 *
 */
import { Described } from './common';
import { VariableSource } from './source';

export type Variable = VariableBase;

export interface VariableBase extends Described {
  shortName?: string;
  displayName: string;
  units?: string;
  unitNotes?: string;
  denominators: VariableBase[];
  depth: number;
  percentLabel: string;
  sources: VariableSource[];
  localeOptions?: Intl.NumberFormatOptions;
  resourcetype: VariableResourceType;
}

export enum VariableResourceType {
  CKANVariable = 'CKANVariable',
  CensusVariable = 'CensusVariable',
}
