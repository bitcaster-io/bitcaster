# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models

from .channel import Channel

logger = logging.getLogger(__name__)


class AssignmentQuerySet(models.QuerySet):
    def get_address(self, klass):
        # if isinstance(klass, Dispatcher):
        #     klass = fqn(klass)
        return super().get(channel__handler=klass).address.address


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='addresses',
                             on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    label = models.CharField(max_length=50)

    class Meta:
        unique_together = ('user', 'label'),
        app_label = 'bitcaster'

    def __str__(self):
        return '{} ({})'.format(self.label, self.address)


class AddressAssignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='assignments',
                             on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                related_name='used_by')
    channel = models.ForeignKey(Channel,
                                on_delete=models.CASCADE,
                                related_name='+')

    objects = AssignmentQuerySet.as_manager()

    class Meta:
        unique_together = ('user', 'channel'),
        app_label = 'bitcaster'

    def __str__(self):
        return str(self.address)
