# -*- coding: utf-8 -*-

from uuid import uuid4

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import UUIDField
from django.utils.functional import cached_property

from bitcaster import logging
from bitcaster.db.fields import SubscriptionPolicyField
from bitcaster.db.validators import RateLimitValidator
from bitcaster.models.mixins import ReverseWrapperMixin

from .application import Application
from .base import AbstractModel

logger = logging.getLogger(__name__)


class Event(ReverseWrapperMixin, AbstractModel):
    """Event is something that can happen into an Application."""
    uuid = UUIDField(default=uuid4, editable=False)
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    related_name='events')
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField(null=True, blank=True)
    allowed_origins = ArrayField(models.GenericIPAddressField(max_length=50),
                                 blank=True,
                                 null=True)
    group = models.CharField(max_length=30, null=True, blank=True)
    arguments = JSONField(null=True, blank=True)
    enabled = models.BooleanField(default=False)
    rate_limit = models.CharField(max_length=100,
                                  null=True, default=None, blank=True,
                                  validators=[RateLimitValidator()])
    channels = models.ManyToManyField('bitcaster.Channel',
                                      # through='bitcaster.EventChannel'
                                      )
    subscription_policy = SubscriptionPolicyField()

    class Meta:
        app_label = 'bitcaster'
        unique_together = ('application', 'name')
        ordering = ('name', 'id')

    class Reverse:
        pattern = 'app-event-{op}'
        args = ['application.organization.slug', 'application.slug', 'id']

    def __str__(self):
        return f'{self.application.name}:{self.name}'

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     super().save(force_insert, force_update, using, update_fields)
    #
    # def clean(self):
    #     super().clean()

    @cached_property
    def valid_channels(self):
        return self.channels.filter(messages__enabled=True)

    @cached_property
    def enabled_channels(self):
        return self.channels.filter(enabled=True)

    def check_enabled(self):
        original = self.enabled
        if original:
            self.enabled = self.valid_channels.exists()
            if self.enabled != original:
                self.save()

    # def get_message(self, channel):
    #     return self.messages.get(channels=channel)
    #
    # def emit(self, context, fail_silently=True):
    #     return emit_event.delay(self, context)
