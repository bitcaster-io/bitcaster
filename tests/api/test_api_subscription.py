from typing import TYPE_CHECKING, Generator, TypedDict

import contextlib

from rest_framework.test import APIClient

import pytest
from testutils.factories import (
    ApiKeyFactory,
    AssignmentFactory,
    ChannelFactory,
    EventFactory,
    MessageTemplateFactory,
    NotificationFactory,
)
from testutils.perms import key_grants

from bitcaster.auth.constants import Grant
from bitcaster.models.choices import FILTERING_SUBSCRIPTION

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application, Assignment, Channel, Event, Notification, User

    class SubscriptionApiData(TypedDict):
        key: ApiKey
        application: Application
        notification: Notification
        assignment: Assignment
        url: str
        channel: Channel


pytestmark = [pytest.mark.api, pytest.mark.django_db]


@pytest.fixture
def data(admin_user: "User") -> "SubscriptionApiData":
    event: Event = EventFactory(
        application__project__organization__name="org-sub",
        application__project__name="prj-sub",
        application__name="app-sub",
    )
    org = event.application.project.organization
    channel: Channel = ChannelFactory(organization=org)
    MessageTemplateFactory(channel=channel, event=event)
    notification: Notification = NotificationFactory(event=event, policy=FILTERING_SUBSCRIPTION, distribution=None)
    assignment: Assignment = AssignmentFactory(channel=channel)
    key: ApiKey = ApiKeyFactory(
        user=admin_user,
        grants=[],
        application=None,
        project=None,
        organization=org,
    )
    url = "/api/o/{}/p/{}/a/{}/n/{}/subscribe/".format(
        org.slug,
        event.application.project.slug,
        event.application.slug,
        notification.pk,
    )
    return {
        "key": key,
        "application": event.application,
        "notification": notification,
        "assignment": assignment,
        "url": url,
        "channel": channel,
    }


@contextlib.contextmanager
def grants(data: "SubscriptionApiData") -> "Generator[None, None, None]":
    with key_grants(data["key"], [Grant.MANAGE_APPLICATION_USERS], application=data["application"]):
        yield


def _auth_client(data: "SubscriptionApiData") -> APIClient:
    client = APIClient()
    client._key = data["key"]
    client.credentials(HTTP_AUTHORIZATION=f"Key {data['key'].key}")
    return client


def test_subscribe_requires_grant(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    res = client.post(data["url"], data={"assignment": data["assignment"].pk})
    assert res.status_code == 403


def test_subscribe_creates(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        res = client.post(data["url"], data={"assignment": data["assignment"].pk, "active": True})

    assert res.status_code == 201
    assert "subscription" in res.json()

    subscription = data["notification"].subscriptions.get()
    assert subscription.pk == res.json()["subscription"]
    assert subscription.assignment == data["assignment"]
    assert subscription.active is True


def test_subscribe_default_active(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        res = client.post(data["url"], data={"assignment": data["assignment"].pk})

    assert res.status_code == 201
    subscription = data["notification"].subscriptions.get()
    assert subscription.active is True


def test_subscribe_active_false(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        res = client.post(data["url"], data={"assignment": data["assignment"].pk, "active": False})

    assert res.status_code == 201
    subscription = data["notification"].subscriptions.get()
    assert subscription.active is False


def test_subscribe_idempotent(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        first = client.post(data["url"], data={"assignment": data["assignment"].pk})
        second = client.post(data["url"], data={"assignment": data["assignment"].pk})

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.json() == second.json()
    assert data["notification"].subscriptions.count() == 1


def test_subscribe_idempotent_applies_active(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        client.post(data["url"], data={"assignment": data["assignment"].pk, "active": False})
        res = client.post(data["url"], data={"assignment": data["assignment"].pk, "active": True})

    assert res.status_code == 200
    subscription = data["notification"].subscriptions.get()
    assert subscription.active is True


def test_subscribe_existing_with_active_false_deactivates(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        client.post(data["url"], data={"assignment": data["assignment"].pk})
        res = client.post(data["url"], data={"assignment": data["assignment"].pk, "active": False})

    assert res.status_code == 200
    subscription = data["notification"].subscriptions.get()
    assert subscription.active is False


def test_subscribe_invalid_payload(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        res = client.post(data["url"], data={})

    assert res.status_code == 400


def test_subscribe_unknown_assignment(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        res = client.post(data["url"], data={"assignment": 999999})

    assert res.status_code == 404


def test_subscribe_unknown_notification(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    url = data["url"].replace(f"/n/{data['notification'].pk}/", "/n/999999/")
    with grants(data):
        res = client.post(url, data={"assignment": data["assignment"].pk})

    assert res.status_code == 404


def test_subscribe_wrong_application(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    url = data["url"].replace(f"/a/{data['application'].slug}/", "/a/wrong-app/")
    with grants(data):
        res = client.post(url, data={"assignment": data["assignment"].pk})

    assert res.status_code == 403


def test_subscribe_assignment_different_org(data: "SubscriptionApiData") -> None:
    """Assignment from a different organization should be rejected."""
    from testutils.factories import AssignmentFactory, ChannelFactory

    other_channel = ChannelFactory()
    other_assignment = AssignmentFactory(channel=other_channel)
    client = _auth_client(data)
    with grants(data):
        res = client.post(data["url"], data={"assignment": other_assignment.pk})

    assert res.status_code == 404


def test_subscribe_assignment_different_org_via_delete(data: "SubscriptionApiData") -> None:
    """Assignment from a different organization should be rejected on DELETE too."""
    from testutils.factories import AssignmentFactory, ChannelFactory

    other_channel = ChannelFactory()
    other_assignment = AssignmentFactory(channel=other_channel)
    client = _auth_client(data)
    with grants(data):
        res = client.delete(f"{data['url']}?assignment={other_assignment.pk}")

    assert res.status_code == 404


def test_unsubscribe(data: "SubscriptionApiData") -> None:
    from testutils.factories import SubscriptionFactory

    SubscriptionFactory.create(notification=data["notification"], assignment=data["assignment"])
    client = _auth_client(data)
    with grants(data):
        res = client.delete(f"{data['url']}?assignment={data['assignment'].pk}")

    assert res.status_code == 200
    assert res.json() == {"subscription": data["notification"].subscriptions.get().pk}
    subscription = data["notification"].subscriptions.get()
    assert subscription.active is False


def test_unsubscribe_idempotent(data: "SubscriptionApiData") -> None:
    from testutils.factories import SubscriptionFactory

    SubscriptionFactory.create(notification=data["notification"], assignment=data["assignment"])
    client = _auth_client(data)
    with grants(data):
        first = client.delete(f"{data['url']}?assignment={data['assignment'].pk}")
        second = client.delete(f"{data['url']}?assignment={data['assignment'].pk}")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_unsubscribe_missing_subscription(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        res = client.delete(f"{data['url']}?assignment={data['assignment'].pk}")

    assert res.status_code == 404


def test_unsubscribe_missing_assignment_param(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        res = client.delete(data["url"])

    assert res.status_code == 400


def test_unsubscribe_invalid_assignment_param(data: "SubscriptionApiData") -> None:
    client = _auth_client(data)
    with grants(data):
        res = client.delete(f"{data['url']}?assignment=not-an-int")

    assert res.status_code == 400
