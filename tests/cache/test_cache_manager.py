import uuid
from unittest.mock import Mock

from bitcaster.cache.manager import CacheManager


def test_cache():
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")
    value = 8899
    assert manager.get_version("key") == 1
    assert manager.incr_version("key")
    assert manager.get_version("key") == 2

    assert manager.store("key", value)
    assert manager.retrieve("key") == value
    count = manager.count_keys()
    deleted = manager.clear_cache()

    assert count == 1
    assert deleted == 1
