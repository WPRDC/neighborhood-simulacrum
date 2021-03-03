/*
 *
 * Variable types
 *
 */
import { Described } from './common';
import { VariableSource } from './source';

export type Variable = VariableBase;

export interface VariableBase extends Described {
  units: string;
  unitNotes: string;
  denominators: VariableBase[];
  depth: number;
  percentLabel: string;
  sources: VariableSource[];
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
