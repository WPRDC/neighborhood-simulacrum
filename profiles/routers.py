# https://docs.djangoproject.com/en/3.2/topics/db/multi-db/#using-routers


class DatastoreRouter(object):
    """ Router for reading from the CKAN datastore """

    def db_for_read(self, model, **hints):
        """ For select models, route queries to the CKAN datastore """
        if hasattr(model, 'USE_DATASTORE') and getattr(model, 'USE_DATASTORE'):
            return 'datastore'
        return None

    def allow_migration(self, db, app_label, model_name=None, **hints):
        """ Prevent migration attempts on the datastore -- shouldn't happen anyway."""
        if db == 'datastore':
            return False
        return None
