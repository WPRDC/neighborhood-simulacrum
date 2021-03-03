/*
 *
 * Source types
 *
 */
import { Described } from './common';

export interface SourceBase extends Described {
  infoLink: string;
}

export interface CensusSource extends SourceBase {
  dataset: string;
}

export interface CensusVariableSource extends CensusSource {
  formula: string;
}

export interface CKANSource extends SourceBase {
  packageId: string;
  resourceId: string;
}

export interface CKANVariableSource extends CKANSource {}

export type VariableSource = CensusVariableSource | CKANVariableSource;
