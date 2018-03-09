# -*- coding: utf-8 -*-
"""
bitcaster / locks
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

import redis_lock
from redis import StrictRedis

logger = logging.getLogger(__name__)

conn = StrictRedis()


def get(key, duration):
    return redis_lock.Lock(conn, key, expire=duration, auto_renewal=True)
