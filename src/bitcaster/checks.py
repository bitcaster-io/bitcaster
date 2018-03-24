# -*- coding: utf-8 -*-
import logging
from pathlib import Path

import redis.exceptions
from constance import config
from django.core.cache import caches
from django.core.checks import Error, register
from django.db import OperationalError, connection

from bitcaster.config.environ import env

logger = logging.getLogger(__name__)


@register(deploy=True)
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
        connection.cursor()
    except OperationalError as e:
        errors.append(
            Error(
                'Database Error',
                hint='check your database configuration',
                obj=None,
                id='bitcaster.E002',
            )
        )

    try:
        caches['default'].set('check', 1)
    except Exception as e:
        errors.append(
            Error(
                "Unable to contact cache backend at '%s'" % env('REDIS_CACHE_URL'),
                hint="check your database configuration",
                obj=None,
                id='bitcaster.E003',
            )
        )
    try:
        caches['lock'].set('check', 1)
    except Exception as e:
        errors.append(
            Error(
                "Unable to contact lock backend at '%s'" % env('REDIS_LOCK_URL'),
                hint=str(e),
                obj=None,
                id='bitcaster.E003',
            )
        )

    for _dir in ('MEDIA_ROOT', 'STATIC_ROOT'):
        if not Path(env(_dir)).exists():
            errors.append(
                Error(
                    f"{_dir} '{Path(env(_dir))}' does not exists",
                    hint='check your configuration',
                    obj=None,
                    id='bitcaster.E004',
                )
            )
    return errors
