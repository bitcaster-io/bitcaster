from strategy_field.utils import fqn

from bitcaster.dispatchers.base import dispatcherManager


def test_registry():
    from bitcaster.dispatchers.test import TestDispatcher

    assert TestDispatcher in dispatcherManager
    assert fqn(TestDispatcher) in dispatcherManager
