from typing import List, Set, Any

from django.db import models
from django.db.models import QuerySet
from markdownx.models import MarkdownxField
from functools import reduce
from profiles.abstract_models import Identified


def reduce_children_qs_to_tags(t: Set[int], child: 'WithTags'):
    return t | recursively_get_child_tag_ids(child)


def reduce_list_of_children_qses_to_tags(t: Set[int], children_qs: QuerySet['WithTags']):
    return t | reduce(reduce_children_qs_to_tags, children_qs, set())


class Tag(Identified):
    pass


def recursively_get_child_tag_ids(obj: 'WithTags') -> Set[int]:
    """ Traverse descendents tree and collect tags """
    # if the object has children, get set of all their tags
    if hasattr(obj, 'children'):
        t = reduce(reduce_list_of_children_qses_to_tags, obj.children, set())
        return t
    # base cases
    # if not children but tags, return those tags as a set
    elif hasattr(obj, 'tags'):
        t = set([tag.id for tag in obj.tags.all()])
        return t
    return set()


class WithTags(models.Model):
    tags = models.ManyToManyField('context.Tag', blank=True)

    # cache tag ids to prevent some duplicate lookups
    _child_tag_ids: Set[int] = None

    class Meta:
        abstract = True

    @property
    def child_tags(self) -> QuerySet['Tag']:
        """ Set of all tags from descendent model instances. """
        if self._child_tag_ids is None:
            tag_ids = recursively_get_child_tag_ids(self)
            self._child_tag_ids = tag_ids
        return Tag.objects.filter(id__in=self._child_tag_ids)


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
    context = models.ManyToManyField('context.ContextItem', blank=True, null=True)

    class Meta:
        abstract = True
