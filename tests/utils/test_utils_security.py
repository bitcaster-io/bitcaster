from typing import TYPE_CHECKING

from datetime import datetime, timedelta

from constance.test import override_config

import pytest
from unittest.mock import Mock

from django.test import override_settings

from bitcaster.exceptions import DecryptionError, KeyExpiredError
from bitcaster.state import state
from bitcaster.utils.security import KeyManager, is_root

if TYPE_CHECKING:
    from pytest_django.fixtures import SettingsWrapper

    from django.test.client import RequestFactory


def test_is_root(rf: "RequestFactory", settings: "SettingsWrapper") -> None:
    request = rf.get("/")
    request.user = Mock()
    assert not is_root(request)
    with override_settings(FLAGS={"IS_ROOT": [("HTTP Request Header", "ROOT_TOKEN=aaa")]}, DEBUG=True):
        with state.configure(request=request):
            request = rf.get("/", HTTP_ROOT_TOKEN="aaa")  # type: ignore[arg-type]
            request.user = Mock()
            assert is_root(request)


def test_key_manager_generate_parse():
    with override_config(SECRET_KEY_SALT="test-salt"):
        km = KeyManager()
        key = km.generate_key(ttl=1, user_id=123)
        data = km.parse_key(key)
        assert data["user_id"] == 123
        assert data["expires_at"] != ""


def test_key_manager_no_ttl():
    with override_config(SECRET_KEY_SALT="test-salt"):
        km = KeyManager()
        key = km.generate_key(ttl=None, user_id=123)
        data = km.parse_key(key)
        assert data["user_id"] == 123
        assert data["expires_at"] == ""


def test_key_manager_expired():
    with override_config(SECRET_KEY_SALT="test-salt"):
        km = KeyManager()
        # Generate a key that expired 1 day ago
        expiration = datetime.now() - timedelta(days=1)
        data = {"expires_at": expiration.isoformat(), "user_id": 123}
        import base64

        from django.core.signing import Signer

        signed_data = Signer(salt="test-salt").sign_object(data).encode()
        key = base64.urlsafe_b64encode(signed_data).decode().rstrip("=")

        with pytest.raises(KeyExpiredError):
            km.parse_key(key)


def test_key_manager_invalid_key():
    with override_config(SECRET_KEY_SALT="test-salt"):
        km = KeyManager()
        with pytest.raises(DecryptionError):
            km.parse_key("invalid-key")
