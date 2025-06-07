from typing import TYPE_CHECKING
from unittest.mock import Mock

from bitcaster.utils.security import is_root

if TYPE_CHECKING:
    from django.test.client import RequestFactory
    from pytest_django.fixtures import SettingsWrapper


def test_is_root(rf: "RequestFactory", settings: "SettingsWrapper") -> None:
    request = rf.get("/")
    request.user = Mock()
    assert not is_root(request)
    settings.ROOT_TOKEN = "aaa"
    request = rf.get("/", **{f"HTTP_{settings.ROOT_TOKEN_HEADER}": "aaa"})  # type: ignore[arg-type]
    request.user = Mock()
    assert is_root(request)
