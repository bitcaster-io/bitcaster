# -*- coding: utf-8 -*-
# import logging

import redis_lock
# logger = logging.getLogger(__name__)
from django.core.cache import caches

# from redis import StrictRedis

cache = caches['lock']
# conn = StrictRedis()


def get(key, timeout=600, blocking_timeout=1) -> redis_lock.Lock:
    """

    :param key:
    :param timeout: lock TTL
    :param blocking_timeout: number of seconds to wait for lock
    :return:
    """
    # return cache.lock(key, expire=timeout)
    return cache.lock(key, timeout=timeout, blocking_timeout=blocking_timeout)
