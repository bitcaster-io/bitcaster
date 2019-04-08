# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from bitcaster.framework.db.fields import EncryptedJSONField

from .base import AbstractModel
from .channel import Channel
from .event import Event
from .mixins import ReverseWrapperMixin
from .user import User

logger = logging.getLogger(__name__)


class SubscriptionQuerySet(models.QuerySet):
    # def enabled(self, *args, **kwargs):
    #     return self.filter(active=True, channel__enabled=True, *args, **kwargs)

    def valid(self, *args, **kwargs):
        return self.filter(enabled=True, channel__enabled=True, *args, **kwargs)


class Subscription(ReverseWrapperMixin, AbstractModel):
    """ """
    STATUSES = Choices(
        (10, 'PROPOSED', _('Admin has sent subscription proposal to user')),
        (20, 'REQUESTED', _('User has requested the subscripiton')),

        (30, 'ACCEPTED', _('User accepted subscription proposal')),
        (40, 'APPROVED', _('Admin approved the subscription request')),
        (50, 'MANAGED', _('Admin subscribed user')),
        (60, 'OWNED', _('User subscribed to event')),
    )
    subscriber = models.ForeignKey(User, models.CASCADE,
                                   # blank=True, null=True,
                                   related_name='subscriptions')

    trigger_by = models.ForeignKey(User, models.CASCADE,
                                   related_name='+')

    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name='subscriptions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
                                related_name='linked_subscriptions')
    enabled = models.BooleanField(default=True)
    config = EncryptedJSONField(null=True, blank=True)
    status = models.IntegerField(choices=STATUSES,
                                 default=STATUSES.OWNED)
    errors = models.IntegerField(default=0)
    objects = SubscriptionQuerySet.as_manager()

    class Meta:
        app_label = 'bitcaster'
        unique_together = ('channel', 'subscriber', 'event')
        get_latest_by = 'id'
        verbose_name = _('Subscription')
        verbose_name_plural = _('Subscriptions')

    class Reverse:
        pattern = 'app-event-subscription-{op}'
        args = ['event.application.organization.slug', 'event.application.slug', 'event.id', 'id']

    def __str__(self):
        return 'Subscription to {0.event} via {0.channel}'.format(self)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    @cached_property
    def recipient(self):
        return self.channel.handler.get_recipient_address(self)
    # def update_token(self):
    #     self.deactivation_token = generate_subscription_token(self)
    #
    # def clean(self):
    #     try:
    #         if not self.channel.messages.filter(event=self.event).exists():
    #             raise ValidationError({'channel': 'Channel cannot be used as no messages are configured for it'})
    #     except ObjectDoesNotExist:
    #         raise ValidationError({'channel': 'Cannot save subscription without a channel'})
    #
    #     return super().clean()
