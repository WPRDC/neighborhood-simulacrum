/*
 *
 * Common types
 *
 */
import * as React from 'react';

export interface Described {
  id: string | number;
  name: string;
  slug: string;
  description?: string;
}

export type Datum = number | string | React.ReactNode;
