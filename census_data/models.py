from typing import Optional, TYPE_CHECKING

from django.core import validators
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.utils import timezone

CURRENT_YEAR = timezone.now().year
DATASET_CHOICES = (
    ('CEN', 'Decennial Census'),
    ('ACS5', 'ACS 5-year'),
    ('ACS1', 'ACS 1-year'),
)

if TYPE_CHECKING:
    from geo.models import CensusGeography


class CensusTablePointer(models.Model):
    table_id = models.CharField(max_length=15, blank=True, null=True)
    value_table = models.ForeignKey(
        'CensusTable',
        on_delete=models.CASCADE,
        related_name='value_to_pointer'
    )
    moe_table = models.ForeignKey(
        'CensusTable',
        on_delete=models.CASCADE,
        related_name='moe_to_pointer',
        null=True,
        blank=True,
    )
    dataset = models.CharField(
        max_length=4,
        choices=DATASET_CHOICES,
        default='CEN'
    )

    class Meta:
        unique_together = ('value_table', 'dataset')

    def save(self, *args, **kwargs):
        if not self.table_id:
            self.table_id = self.value_table.table_id if self.dataset == 'CEN' else self.value_table.table_id[:-1]
        if self.dataset == 'CEN' and self.moe_table:
            raise ValidationError('Table pointers for decennial census tables don\'t include margins of error')
        super(CensusTablePointer, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.table_id} ({self.dataset})'

    def get_values_at_geog(self, geog: 'CensusGeography') -> (float, Optional[float]):
        try:
            value = CensusValue.objects.get(geography=geog, census_table=self.value_table).value
        except ObjectDoesNotExist:
            value = None
        try:
            moe = CensusValue.objects.get(geography=geog, census_table=self.moe_table).value
        except ObjectDoesNotExist:
            moe = None
        return value, moe

    def get_values_query(self, geog: 'CensusGeography'):
        return CensusValue.objects.get('')


class CensusTable(models.Model):
    dataset = models.CharField(
        max_length=4,
        choices=DATASET_CHOICES,
        default='CEN'
    )
    year = models.IntegerField(
        validators=[validators.MinValueValidator(2010),
                    validators.MaxValueValidator(CURRENT_YEAR)]
    )
    table_id = models.CharField(max_length=15, db_index=True)
    description = models.CharField(max_length=500, db_index=True)

    class Meta:
        unique_together = ['year', 'dataset', 'table_id']

    def __str__(self):
        return f'({self.description}) {self.table_id} ({self.dataset}:{self.year}) '


class CensusValue(models.Model):
    """
    Stores a single (geography, table, value) tuple
    the the values stored here are a function of the Variable, the Series, and the Geography
    the census table is unique to a Variable-Series combination and is where they're effect comes in
    """
    geography = models.ForeignKey('geo.CensusGeography', on_delete=models.CASCADE, db_index=True)
    census_table = models.ForeignKey('CensusTable', on_delete=models.CASCADE, db_index=True)
    value = models.FloatField(null=True, blank=True)
    raw_value = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        index_together = ('geography', 'census_table',)
        unique_together = ('geography', 'census_table',)

    def __str__(self):
        return f'{self.census_table}/{self.geography} [{self.value}]'
