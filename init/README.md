# Initialization Scripts
This directory will contain various scripts used to prepare systems for use in Profiles.  

## Extra Database Configuration
In addition to what is set up by Django, there are some other database configurations that need to be run by a postgres superuser.  

## Connect to CKAN Datastore
This file will set up a [foreign data wrapper](https://www.postgresql.org/docs/current/postgres-fdw.html) around a connection to your CKAN instance.
1. Modify `connect_datastore.sql` to match the settings for your CKAN instance.
2. Run the file 
```shell
  psql -h <YOUR HOST> -U <YOUR SUPERUSER> -d profiles_backend -f connect_datstore.sql 
```

## Initialize the tile server schema and user
This file will set up a special read only user for the [tile server](https://github.com/urbica/martin). 
1. Provide a password for your maps user in `init_maps.sql`.
2. Run the file
```shell
  psql -h <YOUR HOST> -U <YOUR SUPERUSER> -d profiles_backend -f init_maps.sql 
```