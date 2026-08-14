from typing import TYPE_CHECKING, TypedDict

from datetime import timedelta

from rest_framework import status
from rest_framework.test import APIClient

import pytest

from django.core.exceptions import ValidationError
from django.utils import timezone

from bitcaster.auth.constants import Grant
from bitcaster.models import ApiKey
from bitcaster.models.key import ApiKeyKind

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, User

    Context = TypedDict(
        "Context",
        {"event": Event, "key": ApiKey},
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
    key = ApiKeyFactory(
        user=admin_user,
        grants=[Grant.WEB_TRIGGER],
        application=event.application,
        kind=ApiKeyKind.WEB,
        allowed_origins=[ORIGIN],
    )
    return {"event": event, "key": key}


def _url(event: "Event", event_slug: str | None = None) -> str:
    app = event.application
    prj = app.project
    org = prj.organization
    return f"/api/o/{org.slug}/p/{prj.slug}/a/{app.slug}/e/{event_slug or event.slug}/trigger/"


def _auth(client: APIClient, key: ApiKey) -> None:
    client.credentials(HTTP_AUTHORIZATION=f"Key {key.key}")


def test_web_key_trigger(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    _auth(client, api_key)
    res = client.post(url, data={"context": {"k": "v"}}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED, res.json()


def test_web_key_without_origin_denied(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    _auth(client, api_key)
    res = client.post(url, data={}, format="json")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_web_key_wrong_origin_denied(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    _auth(client, api_key)
    res = client.post(url, data={}, format="json", HTTP_ORIGIN="https://evil.example.com")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_web_key_null_origin_denied(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    _auth(client, api_key)
    res = client.post(url, data={}, format="json", HTTP_ORIGIN="null")
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_web_key_trailing_slash_origin_allowed(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    _auth(client, api_key)
    res = client.post(url, data={}, format="json", HTTP_ORIGIN="https://example.com/")
    assert res.status_code == status.HTTP_201_CREATED, res.json()


def test_web_key_expired_denied(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    ApiKey.objects.filter(pk=api_key.pk).update(expires_at=timezone.now() - timedelta(hours=1))
    _auth(client, api_key)
    res = client.post(url, data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_web_key_revoked_denied(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    ApiKey.objects.filter(pk=api_key.pk).update(is_active=False)
    _auth(client, api_key)
    res = client.post(url, data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


def test_server_key_does_not_require_origin(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    ApiKey.objects.filter(pk=api_key.pk).update(kind=ApiKeyKind.SERVER, grants=[Grant.EVENT_TRIGGER])
    _auth(client, api_key)
    res = client.post(url, data={}, format="json")
    assert res.status_code == status.HTTP_201_CREATED, res.json()


def test_session_superuser_not_web_restricted(client: APIClient, data: "Context", admin_user: "User") -> None:
    url = _url(data["event"])
    client.force_authenticate(user=admin_user)
    res = client.post(url, data={"options": {"filters": {"include": [], "exclude": []}}}, format="json")
    assert res.status_code == status.HTTP_201_CREATED, res.json()


def test_web_key_filters_rejected(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    _auth(client, api_key)
    res = client.post(
        url,
        data={"options": {"filters": {"include": [], "exclude": []}}},
        format="json",
        HTTP_ORIGIN=ORIGIN,
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_web_key_context_too_large(client: APIClient, data: "Context", settings) -> None:
    api_key = data["key"]
    url = _url(data["event"])
    settings.TRIGGER_CONTEXT_MAX_SIZE = 10
    _auth(client, api_key)
    res = client.post(url, data={"context": {"key": "a-very-long-value"}}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_web_key_cannot_list_events(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    app = data["event"].application
    _auth(client, api_key)
    url = f"/api/o/{app.project.organization.slug}/p/{app.project.slug}/a/{app.slug}/e/"
    res = client.get(url, HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_403_FORBIDDEN


def test_web_key_last_used_at_updated(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = _url(data["event"])
    _auth(client, api_key)
    res = client.post(url, data={}, format="json", HTTP_ORIGIN=ORIGIN)
    assert res.status_code == status.HTTP_201_CREATED
    api_key.refresh_from_db()
    assert api_key.last_used_at is not None


@pytest.mark.parametrize(
    "grants,kind,allowed_origins,application",
    [
        ([Grant.WEB_TRIGGER], ApiKeyKind.WEB, [ORIGIN], None),
        ([Grant.EVENT_TRIGGER], ApiKeyKind.WEB, [ORIGIN], "keep"),
        ([Grant.WEB_TRIGGER, Grant.EVENT_AUTO_CREATE], ApiKeyKind.WEB, [ORIGIN], "keep"),
        ([Grant.WEB_TRIGGER], ApiKeyKind.WEB, [], "keep"),
        ([Grant.WEB_TRIGGER], ApiKeyKind.SERVER, [ORIGIN], "keep"),
    ],
)
def test_web_key_clean_validation(application, admin_user: "User", grants, kind, allowed_origins) -> None:
    from testutils.factories import ApplicationFactory, EventFactory

    if application is None:
        app = None
    elif application == "keep":
        app = EventFactory().application
    else:
        app = ApplicationFactory()
    key = ApiKey(
        user=admin_user,
        grants=grants,
        kind=kind,
        allowed_origins=allowed_origins,
        application=app,
    )
    with pytest.raises(ValidationError):
        key.clean()


def test_server_key_with_web_trigger_clean_validation(admin_user: "User") -> None:
    from testutils.factories import EventFactory

    key = ApiKey(
        user=admin_user,
        grants=[Grant.WEB_TRIGGER],
        kind=ApiKeyKind.SERVER,
        application=EventFactory().application,
    )
    with pytest.raises(ValidationError):
        key.clean()


def test_web_key_clean_ok(admin_user: "User") -> None:
    from testutils.factories import EventFactory

    key = ApiKey(
        user=admin_user,
        grants=[Grant.WEB_TRIGGER],
        kind=ApiKeyKind.WEB,
        allowed_origins=[ORIGIN],
        application=EventFactory().application,
    )
    key.clean()  # must not raise
