import logging
from _md5 import md5

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from bitcaster.framework.db.fields import EncryptedJSONField

from .address import AddressAssignment
from .base import AbstractModel
from .channel import Channel
from .event import Event
from .mixins import ReverseWrapperMixin
from .user import User

logger = logging.getLogger(__name__)


class SubscriptionQuerySet(models.QuerySet):
    # def enabled(self, *args, **kwargs):
    #     return self.filter(active=True, channel__enabled=True, *args, **kwargs)

    def check_address(self, *args, **kwargs):
        # TODO: updated this code when Subscription.address will be used directly
        to_disable = []
        for e in self.only('pk', 'enabled').filter(enabled=True):
            if not e.address or e.address.disabled:
                to_disable.append(e.pk)
        if to_disable:
            self.filter(id__in=to_disable).update(enabled=False)
        return to_disable


class Subscription(ReverseWrapperMixin, AbstractModel):
    """ """
    STATUSES = Choices(
        # (10, 'PENDING', _('Subscription process is not completed')),
        (60, 'OWNED', _('User subscribed to event')),
        (50, 'MANAGED', _('Admin subscribed user. Subscription is locked')),
    )
    subscriber = models.ForeignKey(User, models.CASCADE,
                                   related_name='subscriptions')

    trigger_by = models.ForeignKey(User, models.CASCADE,
                                   related_name='+')

    event = models.ForeignKey(Event, on_delete=models.CASCADE,
                              related_name='subscriptions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE,
                                related_name='linked_subscriptions')
    assignment = models.ForeignKey(AddressAssignment,
                                   related_name='subscriptions',
                                   on_delete=models.SET_NULL,
                                   blank=True, null=True)

    enabled = models.BooleanField(default=True)
    config = EncryptedJSONField(null=True, blank=True)
    status = models.IntegerField(choices=STATUSES,
                                 default=STATUSES.OWNED)
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
        return '{0.subscriber} to {0.event} via {0.channel}'.format(self)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super().save(force_insert, force_update, using, update_fields)

    @cached_property
    def recipient(self):
        try:
            return self.assignment.address.address
        except ObjectDoesNotExist:
            return None
        except AttributeError:
            return None

    def get_address(self):
        return self.recipient
        # return self.channel.handler.get_recipient_address(self)

    def get_code(self):
        return md5(f'{self.pk}-{self.channel_id}-{self.event_id}-{self.subscriber.email}'.encode('utf8')).hexdigest()

    def siblings(self):
        return Subscription.objects.filter(subscriber=self.subscriber,
                                           event=self.event).exclude(pk=self.pk)
