CREATE SCHEMA maps;
CREATE USER profiles_maps_user;
ALTER USER profiles_maps_user WITH PASSWORD '';
GRANT CONNECT ON DATABASE profiles_backend TO profiles_maps_user;
GRANT USAGE ON SCHEMA maps TO profiles_maps_user;
GRANT SELECT ON ALL TABLES IN SCHEMA maps TO profiles_maps_user;

GRANT profiles_user to postgres;

-- when profiles generates new map tables and views, give SELECT to the maps user by default
ALTER DEFAULT PRIVILEGES
    FOR USER profiles_user
    IN SCHEMA maps
    GRANT SELECT ON TABLES TO profiles_maps_user;

-- todo: move to a management command
-- Add geom_webmercator for geos missing it
UPDATE geo_geography
SET geom_webmercator = ST_Transform(geom, 3857)
WHERE geom_webmercator IS NULL;