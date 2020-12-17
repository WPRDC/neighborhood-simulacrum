/*
 *
 * Common types
 *
 */

export interface Described {
  id: string | number;
  name: string;
  slug: string;
  description?: string;
}
