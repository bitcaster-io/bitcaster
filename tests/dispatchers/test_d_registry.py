import pytest

from strategy_field.utils import fqn

from bitcaster.dispatchers.base import dispatcherManager

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_registry() -> None:
    from testutils.dispatcher import XDispatcher

    assert XDispatcher in dispatcherManager
    assert fqn(XDispatcher) in dispatcherManager


def test_as_choices() -> None:
    from bitcaster.dispatchers import MailgunDispatcher

    choices = dispatcherManager.as_choices()
    assert choices
    assert all(isinstance(fqn_str, str) and isinstance(name, str) for fqn_str, name in choices)
    assert fqn(MailgunDispatcher) in {fqn_str for fqn_str, _ in choices}
    # second call returns the cached value
    assert dispatcherManager.as_choices() == choices
