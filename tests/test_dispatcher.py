from bitcaster.dispatchers.base import dispatcherManager


def test_registry():
    assert dispatcherManager.get("test").slug == "test"
