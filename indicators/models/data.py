from typing import Iterable, TYPE_CHECKING

from django.contrib.gis.db import models

if TYPE_CHECKING:
    from indicators.data import Datum


class CachedIndicatorData(models.Model):
    """
    This table will store generated indicators for future reuse.
    """
    variable = models.CharField(max_length=128)
    geog = models.CharField(max_length=128)
    time_part_hash = models.CharField(max_length=128)
    value = models.FloatField(null=True, blank=True)
    moe = models.FloatField(null=True, blank=True)
    denom = models.FloatField(null=True, blank=True)
    expiration = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('geog', 'variable', 'time_part_hash')
        indexes = [
            models.Index(fields=['variable', 'time_part_hash', 'geog']),
            models.Index(fields=['expiration'])
        ]

    @staticmethod
    def save_records(records: Iterable['Datum'], expiration=None) -> list['CachedIndicatorData']:
        new_records = [CachedIndicatorData(
            geog=datum.geog.global_geoid,
            variable=datum.variable.slug,
            time_part_hash=datum.time.storage_hash,
            value=datum.value,
            denom=datum.denom,
            moe=datum.moe,
            expiration=expiration,
        ) for datum in records]
        return CachedIndicatorData.objects.bulk_create(new_records)
