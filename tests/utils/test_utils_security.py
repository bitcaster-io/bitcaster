from typing import TYPE_CHECKING
from unittest.mock import Mock

from django.test import override_settings

from bitcaster.state import state
from bitcaster.utils.security import is_root

if TYPE_CHECKING:
    from django.test.client import RequestFactory
    from pytest_django.fixtures import SettingsWrapper


def test_is_root(rf: "RequestFactory", settings: "SettingsWrapper") -> None:
    request = rf.get("/")
    request.user = Mock()
    assert not is_root(request)
    with override_settings(FLAGS={"IS_ROOT": [("HTTP Request Header", "ROOT_TOKEN=aaa")]}, DEBUG=True):
        with state.configure(request=request):
            request = rf.get("/", HTTP_ROOT_TOKEN="aaa")  # type: ignore[arg-type]
            request.user = Mock()
            assert is_root(request)
