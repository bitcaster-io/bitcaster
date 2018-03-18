# -*- coding: utf-8 -*-
import logging

import redis_lock
from redis import StrictRedis

logger = logging.getLogger(__name__)

conn = StrictRedis()


def get(key, duration):
    return redis_lock.Lock(conn, key, expire=duration, auto_renewal=True)
