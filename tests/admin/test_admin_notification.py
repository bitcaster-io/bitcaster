# mypy: disable-error-code="union-attr"
from typing import TYPE_CHECKING, Any

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import Message, Notification


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", db: Any) -> "DjangoTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture()
def notification(django_app_factory: "MixinWithInstanceVariables", db: "Any") -> "Notification":
    from testutils.factories import ChannelFactory, MessageFactory, NotificationFactory

    n = NotificationFactory(
        event__channels=[ChannelFactory(), ChannelFactory()], event__application__project__environments=["development"]
    )
    MessageFactory(notification=n, event=n.event, channel=n.event.channels.first())
    return n


def test_create_notification_template(app: "DjangoTestApp", notification: "Notification") -> None:
    url = reverse("admin:bitcaster_notification_messages", args=[notification.pk])
    res = app.get(url)
    frm = res.forms["messageForm"]
    frm["name"] = "Test Notification Template"
    frm["channel"] = notification.event.channels.last().pk
    frm.submit()

    assert notification.messages.filter(name="Test Notification Template").count() == 1


def test_avoid_duplicates_template(app: "DjangoTestApp", notification: "Notification") -> None:
    from testutils.factories import MessageFactory

    message: "Message" = MessageFactory(notification=notification, event=notification.event)
    url = reverse("admin:bitcaster_notification_messages", args=[notification.pk])
    res = app.get(url)
    frm = res.forms["messageForm"]
    frm["name"] = message.name
    frm["channel"] = message.event.channels.first().pk
    res = frm.submit(expect_errors=True)
    assert res.status_code == 400


def test_edit_check_environments(app: "DjangoTestApp", notification: "Notification") -> None:
    url = reverse("admin:bitcaster_notification_change", args=[notification.pk])
    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["environments"].force_value(["test"])
    res = frm.submit(expect_errors=True)
    assert res.status_code == 200
    assert res.context["adminform"].form.errors == {
        "environments": ["One or more values are not available in the project"]
    }


def test_add_check_environments(app: "DjangoTestApp", notification: "Notification") -> None:
    url = reverse("admin:bitcaster_notification_add")
    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["name"] = "Not2"
    frm["environments"].force_value(["test"])
    res = frm.submit(expect_errors=True)
    assert res.status_code == 200
    assert res.context["adminform"].form.errors == {"event": ["This field is required."]}
    # add missing fields
    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["name"] = "Not2"
    frm["event"].force_value(notification.event.pk)
    frm["distribution"].force_value(notification.distribution.pk)
    frm["environments"].force_value(["test"])
    res = frm.submit(expect_errors=True)
    assert res.status_code == 200
    assert res.context["adminform"].form.errors == {
        "environments": ["One or more values are not available in the project"]
    }

    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["name"] = "Not2"
    frm["event"].force_value(notification.event.pk)
    frm["distribution"].force_value(notification.distribution.pk)
    frm["environments"].force_value(["development"])
    res = frm.submit()
    assert res.status_code == 302
