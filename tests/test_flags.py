import os
from unittest import mock

import pytest
from django.test.client import RequestFactory
from pytest_django.fixtures import SettingsWrapper

from bitcaster.apps import client_ip, development, env_var, header_key, server_address
from bitcaster.state import state


@pytest.mark.parametrize("debug", [True, False])
def test_development(rf: RequestFactory, settings: "SettingsWrapper", debug: bool) -> None:
    settings.DEBUG = debug
    request = rf.get("/", HTTP_HOST="127.0.0.1")
    with state.configure(request=request):
        assert development() is debug


@pytest.mark.parametrize("ip", ["127.0.0.1", "192.168.66.66"])
def test_server_address(rf: RequestFactory, ip: str, settings: "SettingsWrapper") -> None:
    settings.ALLOWED_HOSTS = [ip]
    request = rf.get("/", HTTP_HOST=ip)
    with state.configure(request=request):
        assert server_address(ip)


@pytest.mark.parametrize(
    "subnet, ip, result",
    [
        ("192.168.1.0/24", "192.168.1.1", True),
        ("192.168.1.1/32", "192.168.1.1", True),
        ("192.168.1.1", "192.168.1.1", True),
        ("192.168.1.0/24", "192.168.66.1", False),
        ("192.168.0.0/16", "192.168.1.1", True),
    ],
)
def test_client_ip(rf: RequestFactory, subnet: str, ip: str, result: str) -> None:
    request = rf.get("/", REMOTE_ADDR=ip)
    with state.configure(request=request):
        assert client_ip(subnet) == result


@pytest.mark.parametrize(
    "value, result",
    [
        ("BITCASTER_LOGGING_LEVEL=CRITICAL", True),
        ("BITCASTER_LOGGING_LEVEL=WARN", False),
        ("BITCASTER_LOGGING_LEVEL", True),
        ("ERROR", False),
    ],
)
def test_env_var(value: str, result: str) -> None:
    with mock.patch.dict(os.environ, {"BITCASTER_LOGGING_LEVEL": "CRITICAL"}, clear=True):
        assert env_var(value) == result


@pytest.mark.parametrize(
    "value, result",
    [
        ("CUSTOM_KEY=123", True),
        ("CUSTOM_KEY", True),
        ("CUSTOM_KEY=234", False),
        ("MISSING=222", False),
        ("MISSING", False),
        ("ERROR=[", False),
    ],
)
def test_header_key(rf: "RequestFactory", value: str, result: str) -> None:

    request = rf.get("/", HTTP_CUSTOM_KEY="123")
    with state.configure(request=request):
        assert header_key(value) == result
