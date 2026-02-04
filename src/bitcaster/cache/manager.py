from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from flags.state import flag_enabled

from ..utils.django import get_cache_prefix

if TYPE_CHECKING:
    from collections.abc import Generator

    from django.http import HttpRequest
    from django_redis.client import DefaultClient

HOUR = 60 * 60

epoch = datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
end_date = timezone.now()
day = end_date.day


class CacheManager:
    SEED = "cache:"

    def __init__(self, request: "HttpRequest | None", prefix: str | None = None) -> None:
        self.prefix = prefix or settings.CACHE_PREFIX
        self.request = request
        self.current_namespace = ""
        self.client: "DefaultClient" = cache.client

    def get_version(self, key: str) -> int:
        target = f"{self.prefix}:{key}:version"
        if ret := self.client.get(target):
            return ret

        self.client.set(target, 1)
        return 1

    def incr_version(self, key: str) -> int:
        target = f"{self.prefix}:{key}:version"
        try:
            ret = self.client.incr(target)
        except ValueError:
            self.client.set(target, 1)
            ret = 1
        return ret

    @contextmanager
    def activate_namespace(self, name: str) -> "Generator[CacheManager, None, None]":
        self.current_namespace = name
        yield self
        self.current_namespace = ""

    def get_key(self, key: str) -> str:
        return f"{get_cache_prefix()}{CacheManager.SEED}{self.current_namespace}{self.prefix}:{key}"

    def set_expire_at_midnight(self, key: str) -> None:
        now = timezone.localtime()
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        ttl = int((tomorrow - now).total_seconds())
        self.client.expire(key, ttl)

    def count_keys(self) -> int:
        pattern = self.get_key("*")
        count = 0
        for _ in self.client.iter_keys(search=pattern):
            count += 1
        return count

    def touch(self, key: str, timeout: int | None = None, timeboxed: bool = True) -> datetime:
        now = timezone.now()
        self.client.set(self.get_key(key), now.timestamp(), timeout=timeout)
        return now

    def get_last_touch(
        self,
        key: str,
    ) -> datetime:
        value = self.client.get(self.get_key(key))
        if value is None:
            return epoch
        return datetime.fromtimestamp(value, tz=timezone.get_current_timezone())

    def clear_cache(self) -> int:
        pattern = self.get_key("*")
        deleted = 0
        for key in self.client.iter_keys(search=pattern):
            deleted += self.client.delete(key)
        return deleted

    def store(self, key: str, value: Any, timeout: int | None = None, timeboxed: bool = True) -> None:
        if flag_enabled("DISABLE_CACHE"):
            return
        if timeout and not timeboxed:
            timeout = 25 * HOUR
        try:
            self.client.set(self.get_key(key), value, timeout=timeout)
        except TypeError:
            return
        if timeboxed:
            self.set_expire_at_midnight(self.get_key(key))

    def retrieve(self, key: str) -> Any:
        if flag_enabled("DISABLE_CACHE"):
            return None
        return self.client.get(self.get_key(key))
