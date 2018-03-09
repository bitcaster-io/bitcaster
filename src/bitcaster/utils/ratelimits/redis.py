import hashlib
from time import time

# from bitcaster.exceptions import InvalidConfiguration
from django.core.cache import cache

from .base import RateLimiter


class RedisRateLimiter(RateLimiter):
    window = 60

    def __init__(self, **options):
        self.redis = cache

    def is_limited(self, key, limit, application=None, window=None):
        if window is None:
            window = self.window

        key_hex = hashlib.md5(key).hexdigest()
        bucket = int(time() / window)

        if application:
            key = 'rl:%s:%s:%s' % (key_hex, application.id, bucket)
        else:
            key = 'rl:%s:%s' % (key_hex, bucket)

        result = self.redis.incr(key)
        self.redis.expire(key, window)

        return result.value > limit
