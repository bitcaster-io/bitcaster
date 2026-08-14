import uuid

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

import pytest
from unittest.mock import MagicMock

from bitcaster.api.throttling import SlidingWindowThrottle


class MockView(APIView):
    throttle_classes = [SlidingWindowThrottle]
    permission_classes = [AllowAny]
    throttle_rate = 2
    throttle_window = 60

    def get(self, request: Request) -> Response:
        return Response("OK")


class MockViewSet(viewsets.ViewSet):
    throttle_classes = [SlidingWindowThrottle]
    permission_classes = [AllowAny]
    throttle_rate = 10
    throttle_rate_list = 5  # Line 73 coverage: Class-level action override

    def list(self, request: Request) -> Response:
        return Response("OK")

    @action(detail=False, methods=["post"])
    def trigger(self, request: Request) -> Response:
        return Response("OK")

    trigger.throttle_rate = 2
    trigger.throttle_window = 60


@pytest.fixture
def api_factory() -> APIRequestFactory:
    return APIRequestFactory()


@pytest.mark.django_db
def test_sliding_window_throttle_action_decorator(
    api_factory: APIRequestFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    view = MockViewSet.as_view({"post": "trigger"})
    url = "/fake-endpoint/trigger/"
    unique_id = f"action_{uuid.uuid4()}"
    monkeypatch.setattr(SlidingWindowThrottle, "get_ident", lambda self, request: unique_id)

    for _ in range(2):
        assert view(api_factory.post(url)).status_code == status.HTTP_200_OK
    assert view(api_factory.post(url)).status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_sliding_window_throttle_class_action_override(
    api_factory: APIRequestFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Verify class-level action override (Line 73).
    """
    view = MockViewSet.as_view({"get": "list"})
    url = "/fake-endpoint/"
    unique_id = f"class_override_{uuid.uuid4()}"
    monkeypatch.setattr(SlidingWindowThrottle, "get_ident", lambda self, request: unique_id)

    # Should respect throttle_rate_list = 5
    for _ in range(5):
        assert view(api_factory.get(url)).status_code == status.HTTP_200_OK
    assert view(api_factory.get(url)).status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_sliding_window_authenticated_user(api_factory: APIRequestFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify throttling for authenticated users (Line 89).
    """

    view = MockView.as_view()
    url = "/fake-endpoint/"

    mock_user = MagicMock()
    mock_user.is_authenticated = True
    mock_user.id = 999

    request = api_factory.get(url)
    request.user = mock_user
    request.auth = None  # Ensure we hit the user check, not the auth check

    assert view(request).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_sliding_window_fallback_rejection(api_factory: APIRequestFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify that fallback mechanism also rejects after limit (Line 111).
    """
    mock_caches = MagicMock()
    mock_caches.__getitem__.return_value.client.get_client.side_effect = Exception("Redis Down")
    monkeypatch.setattr("bitcaster.api.throttling.caches", mock_caches)

    view = MockView.as_view()  # rate = 2
    url = "/fake-endpoint/"
    unique_id = f"fallback_rej_{uuid.uuid4()}"
    monkeypatch.setattr(SlidingWindowThrottle, "get_ident", lambda self, request: unique_id)

    assert view(api_factory.get(url)).status_code == status.HTTP_200_OK
    assert view(api_factory.get(url)).status_code == status.HTTP_200_OK
    # 3rd request should hit Line 111 (return False)
    assert view(api_factory.get(url)).status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.django_db
def test_sliding_window_web_key_per_key_and_ip(api_factory: APIRequestFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Web credentials (WEB API keys / client tokens) are throttled per key AND IP.
    """
    from testutils.factories import ApiKeyFactory

    from bitcaster.auth.constants import Grant
    from bitcaster.models.key import ApiKeyKind

    mock_caches = MagicMock()
    mock_caches.__getitem__.return_value.client.get_client.side_effect = Exception("Redis Down")
    monkeypatch.setattr("bitcaster.api.throttling.caches", mock_caches)

    key = ApiKeyFactory(grants=[Grant.WEB_TRIGGER], kind=ApiKeyKind.WEB, allowed_origins=["https://example.com"])

    view = MockView.as_view()  # rate = 2
    url = "/fake-endpoint/"

    def request_for(ip: str):
        req = api_factory.get(url, REMOTE_ADDR=ip)
        req._force_auth_user = key.user
        req._force_auth_token = key
        return req

    assert view(request_for("1.1.1.1")).status_code == status.HTTP_200_OK
    assert view(request_for("1.1.1.1")).status_code == status.HTTP_200_OK
    # same key + same IP exceeds the limit
    assert view(request_for("1.1.1.1")).status_code == status.HTTP_429_TOO_MANY_REQUESTS
    # same key + different IP gets a fresh bucket
    assert view(request_for("2.2.2.2")).status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_sliding_window_client_token_per_key_and_ip(
    api_factory: APIRequestFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Client tokens are throttled per token AND IP.
    """
    from testutils.factories import ClientTokenFactory

    mock_caches = MagicMock()
    mock_caches.__getitem__.return_value.client.get_client.side_effect = Exception("Redis Down")
    monkeypatch.setattr("bitcaster.api.throttling.caches", mock_caches)

    token = ClientTokenFactory(allowed_origins=["https://example.com"])

    view = MockView.as_view()  # rate = 2
    url = "/fake-endpoint/"

    def request_for(ip: str):
        req = api_factory.get(url, REMOTE_ADDR=ip)
        req._force_auth_user = token.user
        req._force_auth_token = token
        return req

    assert view(request_for("1.1.1.1")).status_code == status.HTTP_200_OK
    assert view(request_for("1.1.1.1")).status_code == status.HTTP_200_OK
    assert view(request_for("1.1.1.1")).status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert view(request_for("2.2.2.2")).status_code == status.HTTP_200_OK
