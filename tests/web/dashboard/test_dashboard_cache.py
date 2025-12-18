import uuid
from unittest.mock import Mock

from bitcaster.web.dashboard.cache import CacheManager


def test_cache():
    manager = CacheManager(Mock(), f"test-{uuid.uuid4().hex}")
    value = 8899
    assert manager.store("key", value)
    assert manager.retrieve("key") == value
    count = manager.count_keys()
    deleted = manager.clear_cache()

    assert count == 1
    assert deleted == 1
