# -*- coding: utf-8 -*-
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from bitcaster import logging
from bitcaster.db.fields import EncryptedJSONField, EnumField
from bitcaster.models.mixins import ReverseWrapperMixin

from .base import AbstractModel
from .channel import Channel
from .event import Event
from .user import User

logger = logging.getLogger(__name__)


class SubscriptionQuerySet(models.QuerySet):
    # def enabled(self, *args, **kwargs):
    #     return self.filter(active=True, channel__enabled=True, *args, **kwargs)

    def valid(self, *args, **kwargs):
        return self.filter(enabled=True, channel__enabled=True, *args, **kwargs)


class SubscriptionStatus(EnumField):
    a = 1
    b = 2

    PROPOSED = 10
    REQUESTED = 20

    ACCEPTED = 30
    APPROVED = 40
    MANAGED = 50
    OWNED = 60

    @classmethod
    def as_choices(cls):
        return sorted([(int(cls.PROPOSED), _('Admin has sent subscription proposal to user')),
                       (int(cls.REQUESTED), _('User has requested the subscripiton')),

                       (int(cls.ACCEPTED), _('User accepted subscription proposal')),
                       (int(cls.APPROVED), _('Admin approved the subscription request')),
                       (int(cls.MANAGED), _('Admin subscribed user')),
                       (int(cls.OWNED), _('User subscribed to event')),
                       ])


class Subscription(ReverseWrapperMixin, AbstractModel):
    """ """
    subscriber = models.ForeignKey(User, models.CASCADE,
                                   # blank=True, null=True,
                                   related_name='subscriptions')

    trigger_by = models.ForeignKey(User, models.CASCADE,
                                   related_name='+')

    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name='subscriptions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    enabled = models.BooleanField(default=True)
    config = EncryptedJSONField(null=True, blank=True)
    status = models.IntegerField(choices=SubscriptionStatus.as_choices(),
                                 default=SubscriptionStatus.OWNED)

    objects = SubscriptionQuerySet.as_manager()

    class Meta:
        app_label = 'bitcaster'
        unique_together = ('channel', 'subscriber', 'event')
        get_latest_by = 'id'

    class Reverse:
        pattern = 'app-event-subscription-{op}'
        args = ['event.application.organization.slug', 'event.application.slug', 'event.id', 'id']

    def __str__(self):
        return 'Subscription {0.subscriber} on {0.event} via {0.channel}'.format(self)

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
