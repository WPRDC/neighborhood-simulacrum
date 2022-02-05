from django.core.management.base import BaseCommand


# The purpose of this command is kinda of hacky.  We use this in a cron job to allow django to read from
# CKAN datasets that we don't publish for UX reasons (i.e. a dataset that is an undocumented and in a not
# user-friendly format for use in this app that is otherwise shared or sharable in another format).

# !!!! DO NOT use this for sensitive data, !!!!!
# !!!! but also don't put sensitive data on the OPEN DATA portal in the first place !!!!!

class Command(BaseCommand):
    help = "Temporarily allow read access to private datastore tables."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # todo: add setting that has list of private datastore datasets
        # todo: using that and the CKAN API key setting, run through all the datasets and make them public

        # todo: outside django set up cronjob to run this every 5 mins
        pass
