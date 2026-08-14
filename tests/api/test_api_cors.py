from rest_framework.test import APIClient

import pytest

from django.test import override_settings

pytestmark = [pytest.mark.api, pytest.mark.django_db]

ORIGIN = "https://example.com"


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def settings(settings) -> None:
    settings.CORS_ALLOWED_ORIGINS = [ORIGIN]
    settings.CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS"]
    settings.CORS_ALLOW_HEADERS = ["authorization", "content-type"]
    settings.CORS_PREFLIGHT_MAX_AGE = 86400
    settings.CORS_ALLOW_CREDENTIALS = False


def test_allowed_origin_gets_headers(client: APIClient, settings) -> None:
    res = client.get("/api/raw/", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == 200
    assert res["Access-Control-Allow-Origin"] == ORIGIN
    assert "Origin" in res["Vary"]


def test_disallowed_origin_gets_no_headers(client: APIClient, settings) -> None:
    res = client.get("/api/raw/", HTTP_ORIGIN="https://evil.example.com")
    assert res.status_code == 200
    assert "Access-Control-Allow-Origin" not in res


def test_no_origin_gets_no_headers(client: APIClient, settings) -> None:
    res = client.get("/api/raw/")
    assert res.status_code == 200
    assert "Access-Control-Allow-Origin" not in res


def test_non_api_path_gets_no_headers(client: APIClient, settings) -> None:
    res = client.get("/", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == 200
    assert "Access-Control-Allow-Origin" not in res


def test_preflight_allowed(client: APIClient, settings) -> None:
    res = client.options("/api/raw/", HTTP_ORIGIN=ORIGIN, HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET")
    assert res.status_code == 200
    assert res["Access-Control-Allow-Origin"] == ORIGIN
    assert res["Access-Control-Allow-Methods"] == "GET, POST, OPTIONS"
    assert "authorization" in res["Access-Control-Allow-Headers"]
    assert res["Access-Control-Max-Age"] == "86400"


def test_preflight_disallowed(client: APIClient, settings) -> None:
    res = client.options("/api/raw/", HTTP_ORIGIN="https://evil.example.com", HTTP_ACCESS_CONTROL_REQUEST_METHOD="GET")
    assert res.status_code == 200
    assert "Access-Control-Allow-Origin" not in res


def test_allowed_origin_credentials_header(client: APIClient, settings) -> None:
    with override_settings(CORS_ALLOW_CREDENTIALS=True):
        res = client.get("/api/raw/", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == 200
    assert res["Access-Control-Allow-Origin"] == ORIGIN
    assert res["Access-Control-Allow-Credentials"] == "true"


def test_preflight_without_request_method_passes_through(client: APIClient, settings) -> None:
    res = client.options("/api/raw/", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == 200
    assert "Access-Control-Allow-Origin" not in res
