from typing import TYPE_CHECKING, Any

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .utils import django_prefix

if TYPE_CHECKING:
    from django.http import HttpRequest

HOUR = 60 * 60

end_date = timezone.now()
day = end_date.day


class CacheManager:
    SEED = "cache:"

    def __init__(self, request: "HttpRequest", prefix: str | None = None) -> None:
        self.prefix = prefix or settings.CACHE_PREFIX
        self.request = request

    def count_keys(self) -> int:
        client = cache.client.get_client()
        pattern = f"{django_prefix()}{CacheManager.SEED}{self.prefix}*"
        count = 0
        for _ in client.scan_iter(match=pattern):
            count += 1
        return count

    def clear_cache(self) -> int:
        client = cache.client.get_client()
        pattern = f"{django_prefix()}{CacheManager.SEED}{self.prefix}*"
        deleted = 0
        for key in client.scan_iter(match=pattern):
            deleted += client.delete(key)
        return deleted

    def store(self, key: str, value: Any) -> None:
        today = timezone.now()
        day = today.day
        return cache.set(f"{self.SEED}{self.prefix}:{key}:{day}", value, timeout=25 * HOUR)

    def retrieve(self, key: str) -> Any:
        today = timezone.now()
        day = today.day
        return cache.get(f"{self.SEED}{self.prefix}:{key}:{day}")
