from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from bitcaster.models import Message, Notification


@pytest.fixture()
def app(django_app_factory, db):
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture()
def notification(django_app_factory, db):
    from testutils.factories import ChannelFactory, MessageFactory, NotificationFactory

    n = NotificationFactory(event__channels=[ChannelFactory()])
    MessageFactory(notification=n, event=n.event, channel=n.event.channels.first())
    return n


def test_create_template(app, notification: "Notification") -> None:
    url = reverse("admin:bitcaster_notification_messages", args=[notification.pk])
    res = app.get(url)
    frm = res.forms["messageForm"]
    frm["name"] = "Test Template"
    frm["channel"] = notification.event.channels.first().pk
    frm.submit()

    assert notification.messages.filter(name="Test Template").count() == 1


def test_avoid_duplicates_template(app, notification: "Notification") -> None:
    from testutils.factories import MessageFactory

    message: "Message" = MessageFactory(notification=notification, event=notification.event)
    url = reverse("admin:bitcaster_notification_messages", args=[notification.pk])
    res = app.get(url)
    frm = res.forms["messageForm"]
    frm["name"] = message.name
    frm["channel"] = message.event.channels.first().pk
    res = frm.submit(expect_errors=True)
    assert res.status_code == 400
