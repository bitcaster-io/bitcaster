from typing import TYPE_CHECKING, TypedDict

from rest_framework import status
from rest_framework.test import APIClient

import pytest
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


@pytest.fixture
def client(admin_user: "User") -> APIClient:
    return APIClient()


@pytest.fixture
def data(admin_user: "User") -> "Context":
    from testutils.factories import ApiKeyFactory, EventFactory

    event: "Event" = EventFactory.create()
    key = ApiKeyFactory.create(user=admin_user, grants=[], application=event.application)
    return {
        "event": event,
        "key": key,
        "user": admin_user,
    }


def test_profile_me(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = "/api/me/"

    # no token provided
    res = client.get(url, data={})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    # token with wrong grants
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    res = client.get(url)
    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert res.json() == {"detail": "You do not have permission to perform this action. [Grant.USER_PROFILE]"}
    # finally... valid token
    with key_grants(api_key, [Grant.USER_PROFILE]):
        res = client.get(url, data={})
    assert res.status_code == status.HTTP_200_OK
    assert res.json()


def test_profile_messages(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")

    url = "/api/me/messages/"
    with key_grants(api_key, [Grant.USER_PROFILE]):
        res = client.get(url)
    assert res.status_code == status.HTTP_200_OK


def test_profile_addresses(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")

    url = "/api/me/addresses/"
    with key_grants(api_key, [Grant.USER_PROFILE]):
        res = client.get(url)
    assert res.status_code == status.HTTP_200_OK


def test_profile_unseen(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    url = "/api/me/unseen/"
    with key_grants(api_key, [Grant.USER_PROFILE]):
        res = client.get(url)
    assert res.status_code == status.HTTP_200_OK
