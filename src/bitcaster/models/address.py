# -*- coding: utf-8 -*-
"""
mercury / address
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

from django.conf import settings
from django.db import models

from bitcaster.db.fields import DispatcherField

logger = logging.getLogger(__name__)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='addresses',
                             on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    dispatcher = DispatcherField()

    # dispatcher = StrategyField(verbose_name='Dispatcher',
    #                         import_error=handler_not_found,
    #                         display_attribute='name',
    #                         registry=dispatcher_registry)

    class Meta:
        unique_together = ('user', 'dispatcher')
