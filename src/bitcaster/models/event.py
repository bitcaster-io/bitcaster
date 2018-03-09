# -*- coding: utf-8 -*-

from uuid import uuid4

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import UUIDField

from bitcaster import logging

from .application import Application
from .base import AbstractModel

logger = logging.getLogger(__name__)


class Event(AbstractModel):
    """Event is something that can happen into an Application."""
    uuid = UUIDField(default=uuid4, editable=False)
    application = models.ForeignKey(Application,
                                    on_delete=models.CASCADE,
                                    related_name='events')
    name = models.CharField(max_length=100)

    allowed_origins = ArrayField(models.CharField(max_length=50),
                                 blank=True,
                                 null=True)
    # preferences = JSONField(null=True, blank=True)
    group = models.CharField(max_length=30, null=True, blank=True)
    arguments = JSONField(null=True, blank=True)
    enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('application', 'name')

    def __str__(self):
        return f"{self.name} #{self.pk} "

    # def get_message(self, channel):
    #     return self.messages.get(channels=channel)
    #
    # def emit(self, context, fail_silently=True):
    #     return emit_event.delay(self, context)
