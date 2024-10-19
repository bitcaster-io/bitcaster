from typing import TYPE_CHECKING, TypedDict, cast
from unittest.mock import MagicMock

import pytest
from django.test.client import RequestFactory
from rest_framework import status
from rest_framework.test import APIClient
from testutils.factories.event import EventFactory
from testutils.factories.key import ApiKeyFactory

from bitcaster.api.event import EventList
from bitcaster.api.permissions import ApiKeyAuthentication
from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Event, User
    from bitcaster.types.http import ApiRequest

    Context = TypedDict(
        "Context",
        {"event": Event, "key": ApiKey, "backend": ApiKeyAuthentication, "view": EventList},
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture()
def client() -> APIClient:
    c = APIClient()
    return c


@pytest.fixture()
def key() -> APIClient:
    return ApiKeyFactory(application=None, project=None, grants=[Grant.FULL_ACCESS])


@pytest.fixture()
def context(admin_user: "User") -> "Context":
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
