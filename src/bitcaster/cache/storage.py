from typing import Any

from django.core.cache import cache
from django.db.models import Model, QuerySet
from flags.state import flag_enabled


def qs_to_cache(qs: QuerySet[Model], key: str | None = None) -> list[Any]:
    value = list(qs.values())
    if flag_enabled("DISABLE_CACHE"):
        return value
    key = key or str(hash(qs.query))
    cache.set(key, value)
    return value


def qs_from_cache(qs: QuerySet[Model], key: str | None = None) -> list[Any] | None:
    if flag_enabled("DISABLE_CACHE"):
        return None

    key = key or str(hash(qs.query))
    return cache.get(key)


def qs_del_cache(qs: QuerySet[Model], key: str | None = None) -> int:
    key = key or str(hash(qs.query))
    return cache.delete(key)


def qs_get_or_store(qs: QuerySet[Model, Model], key: str | None = None) -> list[Any]:
    if not (value := qs_from_cache(qs, key=key)):
        value = qs_to_cache(qs, key=key)
    return value
