/**
 *
 * settings.ts
 *
 * This is for defining settings that will apply across varying layers.
 * This primarily reserved for metadata, api, filtering concerns..
 *
 **/

export const censusFpsInExtent = [
  '003', // Allegheny county
  '019',
  '128',
  '007',
  '005',
  '063',
  '129',
  '051',
  '059',
  '125',
  '073',
]; // wrap them in quotes for easy use in sql queries

// for right now, we'll use sql, but if this get's more complex, we'll need a different solution
// this get's put in the SQL queries sent to carto for menuLayers geograhries
export const censusFilter = `countyfp IN (${censusFpsInExtent
  .map(fp => `'${fp}'`)
  .join(',')})`;
