from typing import Any

import pytest
from django.test.client import RequestFactory

from bitcaster.apps import development, server_address
from bitcaster.state import state


@pytest.mark.parametrize("debug", [True, False])
def test_development(rf: RequestFactory, settings: Any, debug: bool) -> None:
    settings.DEBUG = debug
    request = rf.get("/", HTTP_HOST="127.0.0.1")
    with state.configure(request=request):
        assert development() is debug


@pytest.mark.parametrize("ip", ["127.0.0.1", "192.168.66.66"])
def test_server_address(rf: RequestFactory, ip: str, settings: Any) -> None:
    settings.ALLOWED_HOSTS = [ip]
    request = rf.get("/", HTTP_HOST=ip)
    with state.configure(request=request):
        assert server_address(ip)
