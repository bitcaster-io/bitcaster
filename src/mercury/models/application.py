# -*- coding: utf-8 -*-
from uuid import uuid4

from bitfield import BitField
from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import models
from django.db.models import Q, UUIDField
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from timezone_field import TimeZoneField

from mercury import logging
from mercury.models.organization import RESERVED_NAMES, Organization
from mercury.utils import locks
from mercury.utils.retries import TimedRetryPolicy
from mercury.utils.slug import slugify_instance

from .base import AbstractModel

logger = logging.getLogger(__name__)

RESERVED_APPLICATION_NAME = frozenset(RESERVED_NAMES)

RESERVED_APPLICATION_SLUGS = frozenset(RESERVED_NAMES)


class Application(AbstractModel):
    """Application """
    uuid = UUIDField(default=uuid4, editable=False, blank=False, null=False)
    organization = models.ForeignKey(Organization,
                                     related_name='applications',
                                     on_delete=models.CASCADE)
    name = models.CharField(_('Name'),
                            max_length=300,
                            validators=[
                                validators.RegexValidator(r'^[\w -]+$',
                                                          _('Enter a valid name.'),
                                                          'invalid')],
                            unique=True)
    slug = models.SlugField(blank=True)
    timezone = TimeZoneField(default='UTC')
    allowed_origins = ArrayField(models.CharField(max_length=50),
                                 blank=True,
                                 null=True)
    first_event = models.DateTimeField(null=True, editable=False)
    rate_limit_count = models.PositiveIntegerField(null=True)
    rate_limit_window = models.PositiveIntegerField(null=True)
    flags = BitField(flags=(
        # ('has_releases', 'This Project has sent release data'),
    ), default=0, null=True)

    class Meta:
        app_label = 'mercury'
        ordering = ("name", "id")

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        return super().delete(using, keep_parents)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.slug:
            lock = locks.get('slug:application', duration=5)
            with TimedRetryPolicy(10, lock.acquire):
                slugify_instance(self, self.name,
                                 reserved=RESERVED_APPLICATION_SLUGS)
            super(Application, self).save(force_insert, force_update, using, update_fields)
        else:
            super(Application, self).save(force_insert, force_update, using, update_fields)

    @cached_property
    def channels(self):
        from .channel import Channel
        return Channel.objects.filter(Q(application=self) | Q(application__isnull=True))

    @cached_property
    def owner(self):
        import warnings
        warnings.warn("'appplication.owner' has been deprecated.",
                      DeprecationWarning)
        return self.organization.owner

    @property
    def rate_limit(self):
        if self.rate_limit_count and self.rate_limit_window:
            return (self.rate_limit_count, self.rate_limit_window)
        return (0, 0)
