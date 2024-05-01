from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, Message, Notification, Organization

    Context = TypedDict(
        "Context",
        {"notification": Notification, "channel": Channel, "message": Message},
    )


@pytest.fixture()
def app(django_app_factory, db):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context() -> "Context":
    from testutils.factories import (
        ChannelFactory,
        EventFactory,
        MessageFactory,
        NotificationFactory,
    )

    ch = ChannelFactory()
    event = EventFactory(channels=[ch], application__project__organization=ch.organization)
    message = MessageFactory(channel=ch, event=event, organization=ch.organization)

    notification = NotificationFactory(event=event)
    return {
        "notification": notification,
        "channel": ch,
        "message": message,
    }


def test_create_template(app, context) -> None:
    channel: "Channel" = context["channel"]

    notification: "Notification" = context["notification"]
    event: "Event" = notification.event
    org: "Organization" = event.application.project.organization

    url = reverse("admin:bitcaster_organization_templates", args=[org.pk])
    res = app.get(url)
    frm = res.forms["messageForm"]
    frm["name"] = "Test Template"
    frm["channel"] = channel.pk
    frm.submit()

    assert org.message_set.filter(name="Test Template").count() == 1


def test_avoid_duplicates_template(app, context) -> None:
    message: "Message" = context["message"]
    channel: "Channel" = context["channel"]

    notification: "Notification" = context["notification"]
    event: "Event" = notification.event
    org: "Organization" = event.application.project.organization

    url = reverse("admin:bitcaster_organization_templates", args=[org.pk])
    res = app.get(url)
    frm = res.forms["messageForm"]
    frm["name"] = message.name
    frm["channel"] = channel.pk
    res = frm.submit(expect_errors=True)
    assert res.status_code == 400

    assert org.message_set.filter(name=message.name).count() == 1
