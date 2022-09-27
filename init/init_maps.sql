-- create new schema and user
CREATE SCHEMA maps;
CREATE USER profiles_maps_user;
ALTER USER profiles_maps_user WITH PASSWORD '';

-- grant permissions to maps user
GRANT CONNECT ON DATABASE profiles_backend TO profiles_maps_user;
GRANT USAGE ON SCHEMA maps TO profiles_maps_user;
GRANT SELECT ON ALL TABLES IN SCHEMA maps TO profiles_maps_user;
GRANT USAGE ON SCHEMA datastore to profiles_maps_user;
GRANT SELECT ON ALL TABLES IN SCHEMA datastore TO profiles_maps_user;
GRANT EXECUTE ON ALL ROUTINES IN SCHEMA maps to profiles_maps_user;

-- grant permission to django user
GRANT CONNECT ON DATABASE profiles_backend TO profiles_user;
GRANT ALL ON SCHEMA maps TO profiles_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA maps TO profiles_user;
GRANT ALL PRIVILEGES ON ALL ROUTINES IN SCHEMA maps to profiles_user;
GRANT ALL PRIVILEGES ON ALL ROUTINES IN SCHEMA maps to profiles_maps_user;
GRANT profiles_user to postgres;

-- when profiles generates new map tables and views, give SELECT to the maps user by default
ALTER DEFAULT PRIVILEGES
    FOR USER profiles_user
    IN SCHEMA maps
    GRANT SELECT ON TABLES TO profiles_maps_user;

-- todo: move to a management command
-- Add geom_webmercator for geos missing it
UPDATE public.geo_adminregion
SET geom_webmercator = ST_Transform(geom, 3857)
WHERE geom_webmercator IS NULL;