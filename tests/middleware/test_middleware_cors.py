from typing import TYPE_CHECKING, Any

import pytest
from unittest.mock import Mock

from django.http import HttpResponse

from bitcaster.middleware.cors import BrowserCorsMiddleware
from bitcaster.models.key import KeyKind

if TYPE_CHECKING:
    from bitcaster.models import ApiKey

pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture
def public_key(admin_user: "ApiKey") -> "ApiKey":
    from testutils.factories import ApiKeyFactory

    return ApiKeyFactory(
        user=admin_user,
        application=None,
        project=None,
        kind=KeyKind.PUBLIC,
        grants=["EVENT_TRIGGER"],
        origins=["https://example.com"],
    )


def _call(request: Any, get_response: Any = None) -> Any:
    middleware = BrowserCorsMiddleware(get_response or Mock(return_value=Mock(status_code=200)))
    return middleware(request)


def test_preflight_allowed(public_key: "ApiKey", rf: Any) -> None:
    request = rf.options(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://example.com",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
    )
    response = _call(request)
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "https://example.com"
    assert "POST" in response["Access-Control-Allow-Methods"]
    assert "authorization" in response["Access-Control-Allow-Headers"]


def test_preflight_denied(public_key: "ApiKey", rf: Any) -> None:
    request = rf.options(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://evil.example",
    )
    response = _call(request)
    assert response.status_code == 403


def test_actual_request_allowed(public_key: "ApiKey", rf: Any) -> None:
    get_response = Mock(return_value=HttpResponse(status=201))
    request = rf.post(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://example.com",
    )
    response = _call(request, get_response)
    assert response.status_code == 201
    assert response["Access-Control-Allow-Origin"] == "https://example.com"
    get_response.assert_called_once()


def test_actual_request_denied(public_key: "ApiKey", rf: Any) -> None:
    get_response = Mock(return_value=HttpResponse(status=201))
    request = rf.post(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://evil.example",
    )
    response = _call(request, get_response)
    assert response.status_code == 403
    get_response.assert_not_called()


def test_missing_origin_denied(public_key: "ApiKey", rf: Any) -> None:
    request = rf.post("/api/o/o/p/p/a/a/e/evt/trigger/", HTTP_AUTHORIZATION=f"Key {public_key.key}")
    response = _call(request)
    assert response.status_code == 403


def test_server_key_passthrough(api_key: "ApiKey", rf: Any) -> None:
    get_response = Mock(return_value=HttpResponse(status=200))
    request = rf.post(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {api_key.key}",
        HTTP_ORIGIN="https://evil.example",
    )
    response = _call(request, get_response)
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response
    get_response.assert_called_once()


def test_no_auth_passthrough(rf: Any) -> None:
    get_response = Mock(return_value=HttpResponse(status=200))
    request = rf.post("/api/o/o/p/p/a/a/e/evt/trigger/", HTTP_ORIGIN="https://example.com")
    response = _call(request, get_response)
    assert response.status_code == 200
    get_response.assert_called_once()
