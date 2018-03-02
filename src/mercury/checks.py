# -*- coding: utf-8 -*-
"""
mercury / checks
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

import redis.exceptions
from constance import config
from django.core.checks import Error, register
from django.db import OperationalError, connection

logger = logging.getLogger(__name__)


@register()
def check(app_configs, **kwargs):
    errors = []
    try:
        config.INITIALIZED
    except redis.exceptions.ConnectionError as e:
        errors.append(
            Error(
                'Unable to contact Redis',
                hint='check your redis configuration',
                obj=None,
                id='bitcaster.E001',
            )
        )
    try:
        cur = connection.cursor()
    except OperationalError as e:
        errors.append(
            Error(
                'Database Error',
                hint='check your database configuration',
                obj=None,
                id='bitcaster.E002',
            )
        )
    return errors
