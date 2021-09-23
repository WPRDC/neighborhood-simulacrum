class DatastoreRouter(object):
    def db_for_read(self, model, **hints):
        """
        Reads go to a randomly-chosen replica.
        """
        return 'datastore'

    def db_for_write(self, model, **hints):
        """
        Writes always go to primary.
        """
        return 'primary'