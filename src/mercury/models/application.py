# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core import validators
from django.db import models
from django.db.models import Q, UUIDField
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from uuid import uuid4

from bitfield import BitField
from timezone_field import TimeZoneField

from mercury import logging

from .base import AbstractModel

logger = logging.getLogger(__name__)


class Application(AbstractModel):
    """Application """
    uuid = UUIDField(default=uuid4, editable=False, blank=False, null=False)
    name = models.CharField(_('Name'),
                            max_length=300,
                            validators=[
                                validators.RegexValidator(r'^[\w -]+$',
                                                          _('Enter a valid name.'),
                                                          'invalid')],
                            unique=True)

    timezone = TimeZoneField(default='UTC')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE,
                              related_name='applications')

    maintainers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                         blank=True,
                                         related_name='+')

    allowed_origins = ArrayField(models.CharField(max_length=50),
                                 blank=True,
                                 null=True)
    first_event = models.DateTimeField(null=True, editable=False)
    # rate_limit_count = models.PositiveIntegerField(null=True)
    # rate_limit_window = models.PositiveIntegerField(null=True)
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

    @cached_property
    def channels(self):
        from .channel import Channel
        return Channel.objects.filter(Q(application=self) | Q(application__isnull=True))

        # @property
        # def owned_channels(self):
        #     return Channel.objects.filter(Q(application=self))
        #
        # @property
        # def monitors(self):
        #     return Monitor.objects.filter(Q(application=self))
