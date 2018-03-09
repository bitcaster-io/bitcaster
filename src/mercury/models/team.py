from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from mercury.db.fields import DeletionStatusField
from mercury.utils import locks
from mercury.utils.retries import TimedRetryPolicy
from mercury.utils.slug import slugify_instance

from .base import AbstractModel
from .organization import Organization


class Team(AbstractModel):
    """
    A team represents a group of individuals which maintain ownership of projects.
    """
    __core__ = True

    organization = models.ForeignKey(Organization,
                                     related_name='teams',
                                     on_delete=models.CASCADE)
    slug = models.SlugField()
    name = models.CharField(_("Name"), max_length=64)
    status = DeletionStatusField()
    date_added = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        unique_together = (('organization', 'slug'), )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            lock = locks.get('slug:team', duration=5)
            with TimedRetryPolicy(10, lock.acquire):
                slugify_instance(self, self.name, organization=self.organization)
            super(Team, self).save(*args, **kwargs)
        else:
            super(Team, self).save(*args, **kwargs)
