from typing import TYPE_CHECKING, TypedDict

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from testutils.factories import ApiKeyFactory, EventFactory
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application, Event, User

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "event": Event,
            "key": ApiKey,
            "user": User,
        },
    )

pytestmark = [pytest.mark.api, pytest.mark.django_db]

# WE DO NOT USE REVERSE HERE. WE NEED TO CHECK ENDPOINTS CONTRACTS


@pytest.fixture()
def client() -> APIClient:
    c = APIClient()
    return c


@pytest.fixture()
def data(admin_user) -> "Context":
    event = EventFactory()
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {
        "app": event.application,
        "event": event,
        "key": key,
        "user": admin_user,
    }


def test_trigger_security(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url = "/api/trigger/{}/trigger/".format(data["event"].slug)
    res = client.post(url, data={})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    client.credentials(HTTP_AUTHORIZATION=f"ApiKey {api_key.key}")
    res = client.post(url, data={})
    assert res.status_code == status.HTTP_403_FORBIDDEN
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.post(url, data={})
        assert res.status_code == status.HTTP_200_OK
