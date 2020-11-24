from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from polymorphic.models import PolymorphicModel

from indicators.models.abstract import Described

THIS_YEAR = timezone.now().year


class Series(Described, PolymorphicModel):
    """  Base class that defines series across variables. """
    pass


class YearSeries(Series):
    """ Series by years """
    year = models.IntegerField(
        default=2010,
        validators=[MinValueValidator(2000),
                    MaxValueValidator(THIS_YEAR)]
    )

    def save(self, *args, **kwargs):
        self.name = str(self.year)
        super(YearSeries, self).save(*args, **kwargs)
