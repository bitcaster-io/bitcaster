from typing import TYPE_CHECKING, TypedDict, cast

from rest_framework import status
from rest_framework.test import APIClient

import pytest
from unittest.mock import MagicMock

from bitcaster.api.event import EventList, EventTrigger
from bitcaster.api.permissions import ApiApplicationPermission, ApiKeyAuthentication
from bitcaster.auth.constants import Grant
from bitcaster.exceptions import InvalidGrantError
from bitcaster.models.key import KeyKind

if TYPE_CHECKING:
    from django.test.client import RequestFactory

    from bitcaster.models import ApiKey, Event, User
    from bitcaster.types.http import ApiRequest

    Context = TypedDict(
        "Context",
        {"event": Event, "key": ApiKey, "backend": ApiKeyAuthentication, "view": EventList},
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.fixture
def key() -> APIClient:
    from testutils.factories import ApiKeyFactory

    return ApiKeyFactory(application=None, project=None, grants=[Grant.FULL_ACCESS])


@pytest.fixture
def context(admin_user: "User") -> "Context":
    from testutils.factories import ApiKeyFactory, EventFactory

    event: "Event" = EventFactory()
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {"event": event, "key": key, "backend": ApiKeyAuthentication(), "view": MagicMock(spec=EventList)}


def test_authenticate(rf: "RequestFactory", context: "Context") -> None:
    b: ApiKeyAuthentication = context["backend"]
    api_key: ApiKey = context["key"]

    req1 = cast("ApiRequest", rf.get("/", {"HTTP_AUTHORIZATION": "Key 123"}))
    assert not b.authenticate(req1)

    req2 = cast("ApiRequest", rf.get("/", headers={"AUTHORIZATION": "Key %s" % api_key.key}))
    assert b.authenticate(req2)


def test_handle_permission_error(client: APIClient, key: "ApiKey") -> None:
    url = f"/api/o/{key.organization.slug}/p/any-slug/"
    client.credentials(HTTP_AUTHORIZATION=f"Key {key.key}")

    res = client.get(url, data={})
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def public_key(admin_user: "User") -> "ApiKey":
    from testutils.factories import ApiKeyFactory, EventFactory

    event = EventFactory()
    return ApiKeyFactory(
        user=admin_user,
        grants=[Grant.EVENT_TRIGGER],
        application=event.application,
        kind=KeyKind.PUBLIC,
        origins=["https://example.com"],
    )


def test_public_key_origin_mismatch(rf: "RequestFactory", public_key: "ApiKey") -> None:
    perm = ApiApplicationPermission()
    view = MagicMock(spec=EventTrigger)
    view.grants = [Grant.EVENT_TRIGGER]
    view.kwargs = {
        "org": public_key.organization.slug,
        "prj": public_key.project.slug,
        "app": public_key.application.slug,
    }
    request = rf.post(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://evil.example",
    )
    request.auth = public_key
    request.user = public_key.user

    with pytest.raises(InvalidGrantError):
        perm.has_permission(request, view)


def test_public_key_origin_match(rf: "RequestFactory", public_key: "ApiKey") -> None:
    perm = ApiApplicationPermission()
    view = MagicMock(spec=EventTrigger)
    view.grants = [Grant.EVENT_TRIGGER]
    view.kwargs = {
        "org": public_key.organization.slug,
        "prj": public_key.project.slug,
        "app": public_key.application.slug,
    }
    request = rf.post(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://example.com",
    )
    request.auth = public_key
    request.user = public_key.user

    assert perm.has_permission(request, view) is True


def test_public_key_wrong_grants(rf: "RequestFactory", public_key: "ApiKey") -> None:
    public_key.grants = [Grant.EVENT_LIST]
    public_key.save()
    perm = ApiApplicationPermission()
    view = MagicMock(spec=EventTrigger)
    view.grants = [Grant.EVENT_TRIGGER]
    view.kwargs = {
        "org": public_key.organization.slug,
        "prj": public_key.project.slug,
        "app": public_key.application.slug,
    }
    request = rf.post(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://example.com",
    )
    request.auth = public_key
    request.user = public_key.user

    with pytest.raises(InvalidGrantError):
        perm.has_permission(request, view)


def test_public_key_requires_application_scope(rf: "RequestFactory", public_key: "ApiKey") -> None:
    public_key.application = None
    public_key.project = None
    public_key.save()
    perm = ApiApplicationPermission()
    view = MagicMock(spec=EventTrigger)
    view.grants = [Grant.EVENT_TRIGGER]
    view.kwargs = {"org": public_key.organization.slug}
    request = rf.post(
        "/api/o/o/p/p/a/a/e/evt/trigger/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://example.com",
    )
    request.auth = public_key
    request.user = public_key.user

    with pytest.raises(InvalidGrantError):
        perm.has_permission(request, view)


def test_public_key_rejected_on_list_events(rf: "RequestFactory", public_key: "ApiKey") -> None:
    perm = ApiApplicationPermission()
    view = MagicMock(spec=EventList)
    view.grants = [Grant.EVENT_LIST]
    view.kwargs = {
        "org": public_key.organization.slug,
        "prj": public_key.project.slug,
        "app": public_key.application.slug,
    }
    request = rf.get(
        "/api/o/o/p/p/a/a/e/",
        HTTP_AUTHORIZATION=f"Key {public_key.key}",
        HTTP_ORIGIN="https://example.com",
    )
    request.auth = public_key
    request.user = public_key.user

    with pytest.raises(InvalidGrantError):
        perm.has_permission(request, view)
