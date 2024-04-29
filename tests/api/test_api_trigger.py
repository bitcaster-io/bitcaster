from typing import TYPE_CHECKING, TypedDict

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from testutils.factories.event import EventFactory
from testutils.factories.key import ApiKeyFactory
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application, Event, Organization, Project, User

    Context = TypedDict(
        "Context",
        {
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
    event: "Event" = EventFactory()
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {
        "event": event,
        "key": key,
        "user": admin_user,
    }


def test_trigger_security(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    evt: "Event" = data["event"]
    app: "Application" = evt.application
    prj: "Project" = app.project
    org: "Organization" = prj.organization

    url = "/api/trigger/o/{}/p/{}/a/{}/e/{}/".format(org.slug, prj.slug, app.slug, evt.slug)
    # no token provided
    res = client.post(url, data={})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    # token with wrong grants
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    res = client.post(url, data={})
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # finally... valid token
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.post(url, data={})
        assert res.status_code == status.HTTP_200_OK


def test_trigger(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    evt: "Event" = data["event"]
    app: "Application" = evt.application
    prj: "Project" = app.project
    org: "Organization" = prj.organization

    url = "/api/trigger/o/{}/p/{}/a/{}/e/{}/".format(org.slug, prj.slug, app.slug, evt.slug)
    # no token provided
    res = client.get(url, data={})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    # token with wrong grants
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    res = client.get(url, data={})
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # finally... valid token
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.get(url, data={})
        assert res.status_code == status.HTTP_200_OK
