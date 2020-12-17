/*
 *
 * Variable types
 *
 */
import { Described } from './common';

export type Variable = VariableBase;

export interface VariableBase extends Described {
  units: string;
  unitNotes: string;
  denominators: VariableBase[];
  depth: number;
  percentLabel: string;
  sources: (string | number)[];
  aggregationMethod: AggregationMethodName;
  field: 'call_no';
  sqlFilter: '';
  resourcetype: '';
}

export enum VariableResourceType {
  CKANVariable = 'CKANVariable',
  CensusVariable = 'CensusVariable',
}

type AggregationMethodName = 'COUNT' | 'AVG' | 'MEDIAN';
