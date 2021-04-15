/**
 *
 * Api.js
 *
 * Functions that handle communicating with backend.
 *
 */
import { DataVizID, GeogIdentifier, GeographyType } from '../types';

export const API_HOST = 'https://api.profiles.wprdc.org';

/**
 * Enum for API endpoints.
 * @readonly
 * @enum string}
 */
enum Endpoint {
  Domain = 'domain',
  // Subdomain = 'subdomain', // might not be necessary to use here
  // Indicator = 'indicator', //   or here
  DataViz = 'data-viz',
  Geog = 'geo',
}

/**
 * Enum for available API methods.
 * @readonly
 * @enum string}
 */
enum Method {
  GET = 'GET',
  // todo: remove these if we decide to not have data entry from this tool
  // POST: 'POST',
  // PUT: 'PUT',
  // DELETE: 'DELETE',
}

/**
 * Default headers to apply to all requests
 *
 * @type {{string: string}}
 */
const baseHeaders = {};

/**
 * Convert an object of paramaters ({param1: value1, etc...}) for a request to
 * a query string ("?param1=value1&p2=v2...")
 *
 * @param {Object} params - object of key value pairs of parameters
 * @returns {string} - url query string representation of `params`
 */
function serializeParams(params?: Record<string, string | number | boolean>) {
  if (!params || !Object.keys(params)) return '';
  return `?${Object.entries(params)
    .map(
      ([key, value]) =>
        `${encodeURIComponent(key)}=${encodeURIComponent(value)}`,
    )
    .join('&')}`;
}

interface APIOptions {
  id?: string | number;
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string | number | boolean>;
  fetchInit?: {};
}

/**
 * Base api call function.
 *
 * @param {Endpoint} endpoint - target for request
 * @param {Method} method - HTTP method to use
 * @param {Object} [options] - optional parameters
 * @param {string | number} [options.id] - id of resource at endpoint to be retrieved
 * @param {Object} [options.params] - url parameters
 * @param {Object} [options.body] - body data to supply to fetch request
 * @param {Object} [options.headers] - HTTP headers to supply to fetch
 * @param {Object} [options.fetchInit] - catchall for other fetch init options
 * @returns {Promise<Response>}
 */
function callApi(endpoint: Endpoint, method: Method, options?: APIOptions) {
  const { id, params, headers, fetchInit } = options || {
    id: undefined,
    params: undefined,
    body: undefined,
    headers: {},
    fetchInit: {},
  };

  const idPath = ['null', 'undefined'].includes(typeof id) ? '' : `${id}/`;
  const urlParams = serializeParams(params);
  const url = `${API_HOST}/${endpoint}/${idPath}${urlParams}`;

  return fetch(url, {
    ...fetchInit,
    ...{
      method,
      headers: { ...baseHeaders, ...headers },
    },
  });
}

/*
 * Helper API functions
 * --------------------
 *  these are the primary interface to the API
 *  and should return a call to `callApi()`
 */
function requestTaxonomy() {
  return callApi(Endpoint.Domain, Method.GET);
}

function requestDataViz(dataVizID: DataVizID, geogIdentifier: GeogIdentifier) {
  const { geogType, geogID } = geogIdentifier;
  return callApi(Endpoint.DataViz, Method.GET, {
    id: dataVizID.id,
    params: { geogType: geogType, geogID: geogID },
  });
}

function requestGeogDescription(geogIdentifier: GeogIdentifier) {
  const { geogType, geogID } = geogIdentifier;
  return callApi(Endpoint.Geog, Method.GET, {
    id: `${geogType}/${geogID}`,
    params: { details: true },
  });
}

function requestGeogList(geogType: GeographyType) {
  return callApi(Endpoint.Geog, Method.GET, { id: geogType });
}

const Api = {
  requestTaxonomy,
  requestDataViz,
  requestGeogDescription,
  requestGeogList,
};
export default Api;
