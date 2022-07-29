# Abstract model classes that are common across apps.

from django.db import models
from markdownx.models import MarkdownxField


class DatastoreDataset(models.Model):
    """ Will route to the ckan datastore"""
    USE_DATASTORE = True
    id = models.IntegerField(db_column='_id', primary_key=True)

    class Meta:
        abstract = True
        db_table: str


class Identified(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=128, unique=True)

    @property
    def title(self):
        return self.name.capitalize()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Described(Identified):
    description = models.TextField(
        verbose_name='Short Description',
        help_text='1 or 2 sentences',
        null=True,
        blank=True,
    )
    full_description = MarkdownxField(
        help_text='Full description with markdown functionality.',
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class TimeStamped(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
