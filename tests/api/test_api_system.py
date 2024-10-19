from typing import TYPE_CHECKING, TypedDict

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from testutils.factories.event import EventFactory
from testutils.factories.key import ApiKeyFactory
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Event, User

    Context = TypedDict(
        "Context",
        {
            "event": Event,
            "key": ApiKey,
            "user": User,
        },
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture()
def client(admin_user: "User") -> APIClient:
    c = APIClient()
    return c


@pytest.fixture()
def data(admin_user: "User") -> "Context":
    event: "Event" = EventFactory()
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {
        "event": event,
        "key": key,
        "user": admin_user,
    }


def test_ping(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = "/api/system/ping/"

    # no token provided
    res = client.get(url, data={})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    # token with wrong grants
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    res = client.get(url)
    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.json() == {"detail": "You do not have permission to perform this action."}
    # finally... valid token
    with key_grants(api_key, Grant.SYSTEM_PING):
        res = client.get(url, data={})
        assert res.status_code == status.HTTP_200_OK
        assert res.json() == {"token": api_key.name}
