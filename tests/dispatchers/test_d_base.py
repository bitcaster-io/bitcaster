import pytest
from unittest.mock import Mock, patch

from strategy_field.utils import fqn

from bitcaster.dispatchers.base import Dispatcher, dispatcherManager
from bitcaster.exceptions import DispatcherError

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "dispatcher" in metafunc.fixturenames:
        m: dict[str, type[Dispatcher]] = {}
        for model in dispatcherManager:
            m[model.name] = model
        metafunc.parametrize("dispatcher", m.values(), ids=m.keys())


def test_registry() -> None:
    from testutils.dispatcher import XDispatcher

    assert XDispatcher in dispatcherManager
    assert fqn(XDispatcher) in dispatcherManager


def test_methods() -> None:
    from testutils.dispatcher import XDispatcher

    assert XDispatcher(Mock()).subscribe(Mock())


def test_errors(dispatcher: "type[Dispatcher]") -> None:
    d = dispatcher(Mock())
    with patch.object(d, "_send", side_effect=Exception()):
        with pytest.raises(DispatcherError):
            d.send(Mock(), Mock())
