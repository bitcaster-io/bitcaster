import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers.base import dispatcherManager

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_registry() -> None:
    from testutils.dispatcher import XDispatcher

    assert XDispatcher in dispatcherManager
    assert fqn(XDispatcher) in dispatcherManager
