import {
  Geog,
  GeogDescriptor,
  GeogIdentifier,
  GeographyType,
  Taxonomy,
} from '../../types';

export interface ExplorerState {
  /** Defines the how the content of the site is organized */
  taxonomy?: Taxonomy;
  taxonomyIsLoading: boolean;
  taxonomyLoadError?: string;

  /** Descriptive data for the geography the user is currently exploring */
  currentGeog?: Geog;
  currentGeogIsLoading: boolean;
  currentGeogLoadError?: string;

  // Navigation todo: consider moving navigation to its own container
  /** The currently selected type of geography (e.g. neighborhood, tract) in the navigation menu */
  selectedGeoLayer: GeogTypeDescriptor;
  /** The currently selected geography in the navigation menu */
  selectedGeogIdentifier: GeogIdentifier;
  /** Caches of list of geographies by keyed type for use in menus */
  geogsListsRecord: Record<GeographyType, GeogDescriptor[]>;
  geogsListsAreLoadingRecord: Record<GeographyType, boolean>;
}

export type ContainerState = ExplorerState;

export interface GeogTypeDescriptor {
  name: string;
  id: GeographyType;
  tableName: string;
  description: string;
}

export interface GeogLoadPayload {
  geogType: GeographyType;
  geogs: GeogDescriptor[];
}
