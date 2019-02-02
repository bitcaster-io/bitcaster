# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from strategy_field.utils import fqn

from bitcaster.db.fields import DispatcherField
from bitcaster.dispatchers import Dispatcher

logger = logging.getLogger(__name__)


class AssignmentQuerySet(models.QuerySet):
    def get_address(self, klass):
        if isinstance(klass, Dispatcher):
            klass = fqn(klass)
        return super().get(dispatcher=klass).address


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
        return self.label


class AddressAssignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='assignments',
                             on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE,
                                related_name='used_by')
    dispatcher = DispatcherField()

    objects = AssignmentQuerySet.as_manager()

    class Meta:
        unique_together = ('dispatcher', 'address'),
        app_label = 'bitcaster'

    # def __str__(self):
    #     return str(self.address)
#
