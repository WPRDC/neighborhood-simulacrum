# Neighborhood Simulacrum
**Open Data Community Indicators Platform**


## Links
[API](https://api.profiles.wprdc.org)  \
[OpenAPI Schema](https://api.profiles.wprdc.org/schema)  
Documentation (
[Swagger UI](https://api.profiles.wprdc.org/schema/swagger-ui/) |
[Redoc](https://api.profiles.wprdc.org/schema/redoc/))  


## System Requirements
1. [Python (^3.8)](https://www.python.org/downloads/)
2. [PostgreSQL (^11)](https://www.postgresql.org/download/) 
3. [Postgis](https://postgis.net/install/)
4. [pip](https://pypi.org/project/pip/)
5. Probably a bunch of other stuff I mistakenly take for granted. Let me know.


## Installation
0. Create a Postgres database with the PostGIS extension added.
1. Clone this code
```shell
git clone https://github.com/WPRDC/neighborhood-simulacra
```
2. Enter the project directory
```shell
cd neighborhood-simulacrum
 ```
3. Create a virtual environment and activate it ([docs](https://docs.python.org/3.9/tutorial/venv.html))
```shell
# make it
$ python3 -m venv env

# activate it
$ . env/bin/activate
```

4. Install required python packages
```shell
$ pip install -r requirements.txt
```

5. Modify [`profiles/local_settings.py.example`](profiles/local_settings.py.example) based on the instructions therein.

6. Configure the database using the projects migrations.
```shell
$ ./manage.py migrate
```

7. Follow the [extra initialization instructions](init/README.md) in `init/` to set up the tile server and CKAN connection.

8. Run your server! :rocket:
```shell
$ ./manage.py runserver
```

Your api will be available at [http://localhost:8000/api](http://localhost:8000/api)  
Your admin interface will be available at [http://localhost:8000/admin](http://localhost:8000/admin)

## Useful Resources / External Docs
### [Django](https://www.djangoproject.com/)
The web framework that the project is built on.

### [Django REST Framework](https://www.django-rest-framework.org/)  
We use the tools from DRF to define our web API.

### [GeoDjango Documentation](https://docs.djangoproject.com/en/3.2/ref/contrib/gis/) 
Since we deal with a lot of geographic data, we use a lot of the geographic tools in Django.

### [Django Polymorphic](https://django-polymorphic.readthedocs.io/en/stable/)
Django polymorphic provides utility classes for standardizing interfaces to polymorphic data models.
