from django.db import models
from markdownx.models import MarkdownxField

from profiles.abstract_models import Identified


class Tag(Identified):
    pass


class WithTags(models.Model):
    tags = models.ManyToManyField('context.Tag', blank=True)

    class Meta:
        abstract = True


class Link(Identified):
    """ A link to a URL """
    url = models.URLField()
    text = models.CharField(max_length=255, help_text='leave blank to use "Name"', blank=True, null=True)


class ContextItem(Identified, WithTags):
    """ Rich Text content that provides context and links """
    DEFAULT = '_'
    INFO = 'I'
    NOTE = 'N'
    WARNING = 'W'
    STOP = 'S'
    DANGER = 'D'
    ERROR = 'E'

    LEVEL_CHOICES = (
        (DEFAULT, 'Default (plain)'),
        (INFO, 'Info (about the data)'),
        (NOTE, 'Note (about our process)'),
        (WARNING, 'Warning (w/ ⚠)'),
        (ERROR, 'Error (with source data)'),
    )

    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    text = MarkdownxField(help_text='Markdown enabled!')
    link = models.ForeignKey(
        Link,
        verbose_name='Primary Link',
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )


class WithContext(models.Model):
    context = models.ManyToManyField('context.ContextItem', )

    class Meta:
        abstract = True
