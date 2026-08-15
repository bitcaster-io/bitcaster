from typing import TYPE_CHECKING, TypedDict

from datetime import timedelta

from rest_framework import status
from rest_framework.test import APIClient

import pytest
from testutils.perms import key_grants

from django.core.management import call_command
from django.utils import timezone

from bitcaster.auth.constants import Grant
from bitcaster.models import ClientToken, Occurrence
from bitcaster.models.key import ApiKeyKind

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Channel, Event, User

    Context = TypedDict(
        "Context",
        {
            "event": Event,
            "key": ApiKey,
            "other_event": Event,
        },
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]

ORIGIN = "https://example.com"


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def data(admin_user: "User", email_channel: "Channel") -> "Context":
    from testutils.factories import ApiKeyFactory, EventFactory

    event: "Event" = EventFactory(channels=[email_channel])
    other_event: "Event" = EventFactory(application=event.application)
    key = ApiKeyFactory(
        user=admin_user,
        grants=[Grant.EVENT_TRIGGER],
        application=event.application,
    )
    return {"event": event, "other_event": other_event, "key": key}


def _app_url(data: "Context") -> str:
    app = data["event"].application
    prj = app.project
    org = prj.organization
    return f"/api/o/{org.slug}/p/{prj.slug}/a/{app.slug}"


def _token_url(data: "Context") -> str:
    return f"{_app_url(data)}/token/"


def _trigger_url(data: "Context", event: "Event | None" = None) -> str:
    return f"{_app_url(data)}/e/{(event or data['event']).slug}/trigger/"


def _auth(client: APIClient, token: str) -> None:
    client.credentials(HTTP_AUTHORIZATION=f"Key {token}")


def _mint(client: APIClient, data: "Context", **payload: object) -> object:
    return client.post(_token_url(data), data=payload, format="json")


def test_mint_client_token(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    res = _mint(client, data, origin=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED, res.json()
    body = res.json()
    assert "token" in body
    assert "expires_at" in body
    assert body["event"] is None


def test_mint_client_token_event_bound(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    res = _mint(client, data, origin=ORIGIN, event=data["event"].slug)
    assert res.status_code == status.HTTP_201_CREATED, res.json()
    assert res.json()["event"] == data["event"].slug


def test_mint_client_token_trigger_flow(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    res = _mint(client, data, origin=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED
    token = res.json()["token"]
    _auth(client, token)
    res = client.post(_trigger_url(data), data={"context": {"k": "v"}}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED, res.json()


def test_mint_requires_origin(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    res = _mint(client, data)
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_mint_invalid_origin(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    res = _mint(client, data, origin="not-a-url")
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_mint_origin_with_path_rejected(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    res = _mint(client, data, origin="https://example.com/page")
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_mint_denied_for_web_key(client: APIClient, data: "Context") -> None:
    web_key = data["key"]
    web_key.grants = [Grant.WEB_TRIGGER]
    web_key.kind = ApiKeyKind.WEB
    web_key.allowed_origins = [ORIGIN]
    web_key.save()
    _auth(client, web_key.key)
    res = _mint(client, data, origin=ORIGIN)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_mint_denied_for_client_token(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    res = _mint(client, data, origin=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED
    _auth(client, res.json()["token"])
    res = _mint(client, data, origin=ORIGIN)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_mint_requires_api_key_auth(client: APIClient, data: "Context") -> None:
    res = _mint(client, data, origin=ORIGIN)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_mint_denied_for_session_auth(client: APIClient, data: "Context", admin_user: "User") -> None:
    client.force_authenticate(user=admin_user)
    res = _mint(client, data, origin=ORIGIN)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_mint_unknown_application_404(client: APIClient, data: "Context") -> None:
    from rest_framework.parsers import JSONParser
    from rest_framework.request import Request
    from rest_framework.test import APIRequestFactory

    from bitcaster.api.token import ClientTokenView
    from bitcaster.models import Application

    key = data["key"]
    app = data["event"].application
    view = ClientTokenView()
    view.kwargs = {
        "org": app.project.organization.slug,
        "prj": app.project.slug,
        "app": app.slug,
    }
    req = APIRequestFactory().post(_token_url(data), data={"origin": ORIGIN}, format="json")
    req._force_auth_user = key.user
    req._force_auth_token = key
    view.get_queryset = lambda: Application.objects.none()
    res = view.post(Request(req, parsers=[JSONParser()]))
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_mint_unknown_event_404(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    res = client.post(_token_url(data), data={"origin": ORIGIN, "event": "does-not-exist"}, format="json")
    assert res.status_code == status.HTTP_404_NOT_FOUND


def test_mint_purges_expired_tokens(client: APIClient, data: "Context") -> None:
    _auth(client, data["key"].key)
    expired = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        token="expired-token",
        expires_at=timezone.now() - timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    assert ClientToken.objects.filter(pk=expired.pk).exists()
    res = _mint(client, data, origin=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED
    assert not ClientToken.objects.filter(pk=expired.pk).exists()


def test_token_expired_denied(client: APIClient, data: "Context") -> None:
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        expires_at=timezone.now() - timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(_trigger_url(data), data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_token_revoked_denied(client: APIClient, data: "Context") -> None:
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
        is_active=False,
    )
    _auth(client, token.token)
    res = client.post(_trigger_url(data), data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_token_without_origin_denied(client: APIClient, data: "Context") -> None:
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(_trigger_url(data), data={}, format="json")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_token_wrong_origin_denied(client: APIClient, data: "Context") -> None:
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(_trigger_url(data), data={}, format="json", HTTP_ORIGIN="https://evil.example.com")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_token_event_bound_rejects_other_event(client: APIClient, data: "Context") -> None:
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        event=data["event"],
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(_trigger_url(data, data["other_event"]), data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_token_event_bound_accepts_bound_event(client: APIClient, data: "Context") -> None:
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        event=data["event"],
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(_trigger_url(data), data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED, res.json()


def test_token_filters_rejected(client: APIClient, data: "Context") -> None:
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(
        _trigger_url(data),
        data={"options": {"filters": {"include": [], "exclude": []}}},
        format="json",
        HTTP_ORIGIN=ORIGIN,
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_token_context_too_large(client: APIClient, data: "Context", settings) -> None:
    settings.TRIGGER_CONTEXT_MAX_SIZE = 10
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(
        _trigger_url(data),
        data={"context": {"key": "a-very-long-value"}},
        format="json",
        HTTP_ORIGIN=ORIGIN,
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_token_last_used_at_updated(client: APIClient, data: "Context") -> None:
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=data["event"].application.project.organization,
        project=data["event"].application.project,
        application=data["event"].application,
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(_trigger_url(data), data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED
    token.refresh_from_db()
    assert token.last_used_at is not None


def test_token_environments_scoping(client: APIClient, data: "Context") -> None:
    event = data["event"]
    event.environments = ["development"]
    event.save()
    token = ClientToken.objects.create(
        user=data["key"].user,
        organization=event.application.project.organization,
        project=event.application.project,
        application=event.application,
        environments=["production"],
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    _auth(client, token.token)
    res = client.post(_trigger_url(data), data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED
    occurrence = Occurrence.objects.get(pk=res.json()["occurrence"])
    assert occurrence.options.get("environs") == ["production"]


def test_cleanup_command_removes_expired(client: APIClient, data: "Context") -> None:
    user = data["key"].user
    app = data["event"].application
    expired = ClientToken.objects.create(
        user=user,
        organization=app.project.organization,
        project=app.project,
        application=app,
        expires_at=timezone.now() - timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    valid = ClientToken.objects.create(
        user=user,
        organization=app.project.organization,
        project=app.project,
        application=app,
        expires_at=timezone.now() + timedelta(hours=1),
        allowed_origins=[ORIGIN],
    )
    call_command("cleanup_client_tokens")
    assert not ClientToken.objects.filter(pk=expired.pk).exists()
    assert ClientToken.objects.filter(pk=valid.pk).exists()


def test_mint_denied_without_event_grant(client: APIClient, data: "Context") -> None:
    with key_grants(data["key"], [Grant.APPLICATION_ADMIN], add=False):
        _auth(client, data["key"].key)
        res = _mint(client, data, origin=ORIGIN)
        assert res.status_code == status.HTTP_403_FORBIDDEN
