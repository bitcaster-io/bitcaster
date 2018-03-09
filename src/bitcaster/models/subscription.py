# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.db import models

from bitcaster import logging
from bitcaster.db.fields import EncryptedJSONField
from bitcaster.utils import generate_subscription_token

from .base import AbstractModel
from .channel import Channel
from .event import Event
from .user import User

logger = logging.getLogger(__name__)


class SubscriptionQuerySet(models.QuerySet):
    def enabled(self, *args, **kwargs):
        return self.filter(active=True, channel__enabled=True, *args, **kwargs)

    def valid(self, *args, **kwargs):
        return self.filter(active=True, channel__enabled=True, *args, **kwargs)


class Subscription(AbstractModel):
    """ """
    subscriber = models.ForeignKey(User, models.CASCADE,
                                   related_name='subscriptions')
    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name='subscriptions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    config = EncryptedJSONField(null=True, blank=True)

    objects = SubscriptionQuerySet.as_manager()
    deactivation_token = models.CharField(max_length=100,
                                          editable=False,
                                          unique=True)
    managed = models.BooleanField(default=False,
                                  help_text="if managed users cannot unsubscribe. "
                                            "But can still change channel")
    locked = models.BooleanField(default=False,
                                 help_text="if locked users cannot change subscription")

    class Meta:
        unique_together = ('channel', 'subscriber')
        get_latest_by = 'id'

    def __str__(self):
        return "Subscription {0.subscriber} on {0.event} via {0.channel}".format(self)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.pk:
            self.update_token()
        super().save(force_insert, force_update, using, update_fields)

    def update_token(self):
        self.deactivation_token = generate_subscription_token(self)

    def clean(self):
        if not self.channel.messages.filter(event=self.event).exists():
            raise ValidationError('Channel cannot be used as no messages are configured for it')
        return super().clean()
