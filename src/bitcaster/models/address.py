# -*- coding: utf-8 -*-
import logging

from django.conf import settings
from django.db import models
from strategy_field.utils import fqn

from bitcaster.db.fields import DispatcherField
from bitcaster.dispatchers import Dispatcher

logger = logging.getLogger(__name__)


class AddressQuerySet(models.QuerySet):
    def get_address(self, klass):
        if isinstance(klass, Dispatcher):
            klass = fqn(klass)
        return super().get(dispatcher=klass).address


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='addresses',
                             on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    dispatcher = DispatcherField()

    objects = AddressQuerySet.as_manager()

    class Meta:
        unique_together = ('user', 'dispatcher')

    def __str__(self):
        return self.address
