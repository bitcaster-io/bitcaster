from typing import TYPE_CHECKING, Any, TypedDict
from unittest.mock import Mock

import pytest
from rest_framework import status
from rest_framework.test import APIClient
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant
from bitcaster.constants import SystemEvent
from bitcaster.tasks import process_occurrence

if TYPE_CHECKING:
    from pytest import MonkeyPatch

    from bitcaster.models import (
        ApiKey,
        Application,
        Assignment,
        Channel,
        Event,
        Notification,
        Organization,
        Project,
        User,
    )

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
def data(admin_user: "User", email_channel: "Channel") -> "Context":
    from testutils.factories import (
        ApiKeyFactory,
        AssignmentFactory,
        EventFactory,
        MessageFactory,
        NotificationFactory,
    )

    event: "Event" = EventFactory(channels=[email_channel], messages=[MessageFactory(channel=email_channel)])
    NotificationFactory(
        distribution__recipients=[AssignmentFactory(channel=email_channel) for __ in range(4)], event=event
    )
    # event: "Event" = n.event
    key = ApiKeyFactory(user=admin_user, grants=[], application=event.application)
    return {
        "event": event,
        "key": key,
        "user": admin_user,
        "url": "/api/o/{}/p/{}/a/{}/e/{}/trigger/".format(
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
    url: str = data["url"]
    res = client.post(url, data={})
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "perm,status_code",
    [
        (Grant.EVENT_TRIGGER, status.HTTP_201_CREATED),
        (Grant.SYSTEM_PING, status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_trigger_permission(client: APIClient, data: "Context", perm: Grant, status_code: int) -> None:
    api_key = data["key"]
    url: str = data["url"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    # no token provided
    with key_grants(api_key, [perm]):
        res = client.post(url, data={})
        assert res.status_code == status_code


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
        assert res.status_code == status.HTTP_201_CREATED, res.json()
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

    url = "/api/o/{}/p/{}/a/{}/e/missing-event/trigger/".format(org.slug, prj.slug, app.slug)
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.post(url, data={"context": event_context}, format="json")
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.data["error"]


def test_trigger_limit_to_receiver(client: APIClient, data: "Context", monkeypatch: "MonkeyPatch") -> None:
    from bitcaster.models import Occurrence

    api_key = data["key"]
    event = data["event"]
    url: str = data["url"]
    n: "Notification" = event.notifications.first()
    recipients: list[Assignment] = list(n.distribution.recipients.all())
    target: Assignment = recipients[0]
    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.post(
            url,
            data={
                "context": {"key": "value"},
                "options": {"limit_to": [target.address.value]},
            },
            format="json",
        )
        assert res.status_code == status.HTTP_201_CREATED, res.json()
        assert res.data["occurrence"]
        o: "Occurrence" = Occurrence.objects.get(pk=res.data["occurrence"])

    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", Mock())
    assert o.options == {"limit_to": [target.address.value]}

    delivered = process_occurrence(o.pk)
    assert delivered == 1
    o.refresh_from_db()
    assert o.data == {"delivered": [target.pk], "recipients": [[target.address.value, target.channel.name]]}


def test_trigger_limit_to_with_wrong_receiver(
    client: APIClient, data: "Context", monkeypatch: "MonkeyPatch", system_objects: Any
) -> None:
    from bitcaster.models import Occurrence

    api_key = data["key"]
    url: str = data["url"]

    client.credentials(HTTP_AUTHORIZATION=f"Key {api_key.key}")
    with key_grants(api_key, Grant.EVENT_TRIGGER):
        res = client.post(
            url,
            data={
                "context": {"key": "value"},
                "options": {"limit_to": ["invalid-address"]},
            },
            format="json",
        )
        assert res.status_code == status.HTTP_201_CREATED, res.json()
        assert res.data["occurrence"]
        o: "Occurrence" = Occurrence.objects.get(pk=res.data["occurrence"])

    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", Mock())
    assert o.options == {"limit_to": ["invalid-address"]}

    delivered = process_occurrence(o.pk)
    assert delivered == 0
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value).count() == 1
