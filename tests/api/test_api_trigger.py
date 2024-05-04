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
            "url": str,
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
        "url": "/api/trigger/o/{}/p/{}/a/{}/e/{}/".format(
            event.application.project.organization.slug,
            event.application.project.slug,
            event.application.slug,
            event.slug,
        ),
    }


def test_trigger_invalid(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url: str = data["url"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")

    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.post(url, data={"context": 22}, format="json")
        assert res.status_code == status.HTTP_400_BAD_REQUEST


def test_trigger_405(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url: str = data["url"]

    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.get(url, data={})
        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


def test_trigger_security(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    url: str = data["url"]
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
        assert res.status_code == status.HTTP_200_OK, res.json()
        assert res.data["occurrence"], res.json()


def test_trigger(client: APIClient, data: "Context") -> None:
    from bitcaster.models import Occurrence

    api_key = data["key"]
    url: str = data["url"]
    event_context = {"key": "value"}
    # no token provided
    res = client.post(url, data={})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED

    # token with wrong grants
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    res = client.post(url, data={})
    assert res.status_code == status.HTTP_403_FORBIDDEN

    # finally... valid token
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.post(url, data={"context": event_context}, format="json")
        assert res.status_code == status.HTTP_200_OK, res.json()
        assert res.data["occurrence"]
        o = Occurrence.objects.get(pk=res.data["occurrence"])
        assert o.context == event_context


def test_trigger_404(client: APIClient, data: "Context") -> None:
    api_key = data["key"]
    event_context = {"key": "value"}

    evt: "Event" = data["event"]
    app: "Application" = evt.application
    prj: "Project" = app.project
    org: "Organization" = prj.organization
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")

    url = "/api/trigger/o/{}/p/{}/a/{}/e/missing-event/".format(org.slug, prj.slug, app.slug)
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.post(url, data={"context": event_context}, format="json")
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.data["error"]
