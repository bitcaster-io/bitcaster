import os
from typing import Any, Optional

import pytest
from django.core.cache import cache
from pytest_django import DjangoAssertNumQueries
from pytest_django.fixtures import SettingsWrapper

from bitcaster.cache.storage import (
    qs_del_cache,
    qs_from_cache,
    qs_get_or_store,
    qs_to_cache,
)
from bitcaster.models import Occurrence


@pytest.fixture()
def data(settings: SettingsWrapper) -> None:
    from testutils.factories import OccurrenceFactory

    settings.FLAGS = {"DISABLE_CACHE": [("boolean", False)]}

    cache.clear()
    OccurrenceFactory()


@pytest.mark.parametrize("key", ["key-1", None])
def test_flag_disable(
    data: Any, settings: SettingsWrapper, django_assert_num_queries: DjangoAssertNumQueries, key: str
) -> None:
    settings.FLAGS = {"DISABLE_CACHE": [("boolean", True)]}
    qs = Occurrence.objects.all()
    assert qs_from_cache(qs, key=key) is None
    with django_assert_num_queries(2):
        assert qs_from_cache(qs, key=key) is None
        assert qs_from_cache(qs, key=key) is None

    with django_assert_num_queries(3):
        assert qs_get_or_store(qs, key=key)


@pytest.mark.parametrize("key", ["key-1", None])
def test_store_to_cache(data: Any, django_assert_num_queries: DjangoAssertNumQueries, key: Optional[None]) -> None:
    qs = Occurrence.objects.all()
    if key:
        key = f"{key}-{os.environ.get('PYTEST_XDIST_WORKER', '')}"
    with django_assert_num_queries(2):
        ret = qs_to_cache(qs, key=key)
    assert ret == list(qs.values())


@pytest.mark.parametrize("key", ["key-1", None])
def test_get_from_cache(data: Any, django_assert_num_queries: DjangoAssertNumQueries, key: Optional[None]) -> None:
    if key:
        key = f"{key}-{os.environ.get('PYTEST_XDIST_WORKER', '')}"
    qs = Occurrence.objects.all()
    qs_to_cache(qs, key=key)
    with django_assert_num_queries(1):
        assert qs_from_cache(qs, key=key)


@pytest.mark.parametrize("key", ["key-1", None])
def test_qs_get_or_store(data: Any, django_assert_num_queries: DjangoAssertNumQueries, key: Optional[None]) -> None:
    if key:
        key = f"{key}-{os.environ.get('PYTEST_XDIST_WORKER', '')}"
    qs = Occurrence.objects.filter()[:1]
    with django_assert_num_queries(3):
        assert qs_get_or_store(qs, key=key)

    with django_assert_num_queries(1):
        assert qs_get_or_store(qs, key=key)


@pytest.mark.parametrize("key", ["key-1", None])
def test_qs_delete(data: Any, django_assert_num_queries: DjangoAssertNumQueries, key: Optional[None]) -> None:
    if key:
        key = f"{key}-{os.environ.get('PYTEST_XDIST_WORKER', '')}"
    qs = Occurrence.objects.filter()[:1]
    qs_to_cache(qs, key=key)
    with django_assert_num_queries(0):
        assert qs_del_cache(qs, key=key)
