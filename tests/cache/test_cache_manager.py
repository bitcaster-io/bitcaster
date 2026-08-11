import uuid

from unittest.mock import Mock, patch

from bitcaster.cache.manager import CacheManager


def test_cache_manager():
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")
    value = 8899
    assert manager.get_version("key") == 1
    assert manager.incr_version("key")
    assert manager.get_version("key") == 2

    manager.store("key", value)  # store returns None
    assert manager.retrieve("key") == value
    count = manager.count_keys()
    deleted = manager.clear_cache()

    assert count == 1
    assert deleted == 1


def test_incr_version_value_error():
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")
    # Mock the client to raise ValueError on incr
    manager.client = Mock()
    manager.client.incr.side_effect = ValueError

    assert manager.incr_version("key") == 1
    manager.client.set.assert_called_with(f"{manager.prefix}:key:version", 1)


def test_delete():
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")
    manager.client = Mock()

    manager.delete("key")
    manager.client.delete.assert_called_once_with(manager.get_key("key"))


def test_activate_namespace():
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")
    assert manager.current_namespace == ""

    with manager.activate_namespace("ns1"):
        assert manager.current_namespace == "ns1"
        key = manager.get_key("key")
        assert "ns1" in key

    assert manager.current_namespace == ""


@patch("bitcaster.cache.manager.flag_enabled")
def test_store_disable_cache(mock_flag_enabled):
    mock_flag_enabled.return_value = True
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")

    assert manager.store("key", "value") is None

    manager.client = Mock()
    manager.store("key", "value")
    manager.client.set.assert_not_called()


@patch("bitcaster.cache.manager.flag_enabled")
def test_retrieve_disable_cache(mock_flag_enabled):
    mock_flag_enabled.return_value = True
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")

    assert manager.retrieve("key") is None

    manager.client = Mock()
    manager.retrieve("key")
    manager.client.get.assert_not_called()


def test_store_timeout_not_timeboxed():
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")
    manager.client = Mock()

    manager.store("key", "value", timeboxed=False)

    # Check if timeout was updated to 25 * 3600 (90000)
    manager.client.set.assert_called()
    args, kwargs = manager.client.set.call_args
    assert kwargs["timeout"] == 25 * 60 * 60

    # Verify expire was NOT called
    manager.client.expire.assert_not_called()


def test_store_timeout_not_timeboxed_explicit_timeout():
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")
    manager.client = Mock()

    manager.store("key", "value", timeout=100, timeboxed=False)

    # Explicit timeout is honored when not timeboxed
    manager.client.set.assert_called()
    args, kwargs = manager.client.set.call_args
    assert kwargs["timeout"] == 100

    # Verify expire was NOT called
    manager.client.expire.assert_not_called()


def test_store_timeboxed():
    manager = CacheManager(Mock(), prefix=f"test-{uuid.uuid4().hex}")
    manager.client = Mock()

    manager.store("key", "value", timeboxed=True)

    manager.client.expire.assert_called()
