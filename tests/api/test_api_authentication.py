from typing import TYPE_CHECKING, TypedDict
from unittest.mock import MagicMock

import pytest
from rest_framework.test import APIClient
from testutils.factories.event import EventFactory
from testutils.factories.key import ApiKeyFactory

from bitcaster.api.event import EventList
from bitcaster.api.permissions import ApiKeyAuthentication

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Event

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
def context(admin_user) -> "Context":
    event: "Event" = EventFactory()
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {"event": event, "key": key, "backend": ApiKeyAuthentication(), "view": MagicMock(spec=EventList)}


def test_authenticate(rf, context: "Context") -> None:
    b: ApiKeyAuthentication = context["backend"]
    api_key: ApiKey = context["key"]

    req = rf.get("/", {"HTTP_AUTHORIZATION": "Key 123"})
    assert not b.authenticate(req)

    req = rf.get("/", headers={"AUTHORIZATION": "Key %s" % api_key.key})
    assert b.authenticate(req)
