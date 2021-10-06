CREATE EXTENSION IF NOT EXISTS postgres_fdw;
CREATE EXTENSION IF NOT EXISTS postgis;

-- create server connection on profiles end
CREATE SERVER IF NOT EXISTS datastore
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host 'YOUR CKAN POSTGRES HOST', dbname 'YOUR DATASTORE DBNAME', port '5432');

-- map our user accounts to the datastore account
CREATE USER MAPPING IF NOT EXISTS FOR profiles_user
        SERVER datastore
        OPTIONS (user 'datastore', password 'YOUR DATASTORE PASSWORD');


CREATE USER MAPPING FOR postgres
        SERVER datastore
        OPTIONS (user 'datastore', password 'YOUR DATASTORE PASSWORD');

-- we need this nested type in the public schema for the import to work
CREATE TYPE public.nested AS
(
    json  json,
    extra text
);

-- import the datastore's public shema into a local one
CREATE SCHEMA IF NOT EXISTS datastore; -- the local one
IMPORT FOREIGN SCHEMA public
    FROM SERVER datastore INTO datastore;

-- ?? dunno why this was here
-- ?? ALTER TYPE NESTED OWNER TO ckan;

-- test pulling gdata
SELECT * FROM "datastore"."bb9a7972-981c-4026-8483-df8bdd1801c2";
-- give the django db user privileges to the linked schema
GRANT USAGE ON FOREIGN SERVER datastore TO profiles_user;
GRANT USAGE ON SCHEMA datastore TO profiles_user;
GRANT ALL ON ALL TABLES IN SCHEMA datastore TO profiles_user;