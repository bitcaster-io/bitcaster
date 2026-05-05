# mypy: disable-error-code="union-attr"
from typing import TYPE_CHECKING, Any

import json

import pytest
from testutils.helpers import assert_form_error

from django.urls import reverse

from bitcaster.models import Notification
from bitcaster.models.choices import FILTERING_DYNAMIC, FILTERING_EXTERNAL, FILTERING_NONE

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import MessageTemplate


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", db: Any) -> "DjangoTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def notification(django_app_factory: "MixinWithInstanceVariables", db: "Any") -> "Notification":
    from testutils.factories import ChannelFactory, MessageTemplateFactory, NotificationFactory

    n = NotificationFactory(
        event__channels=[ChannelFactory(), ChannelFactory()], event__application__project__environments=["development"]
    )
    MessageTemplateFactory(notification=n, event=n.event, channel=n.event.channels.first())
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
    from testutils.factories import MessageTemplateFactory

    message: "MessageTemplate" = MessageTemplateFactory(notification=notification, event=notification.event)
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
    frm.fields["environments"][0].value = "test"
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
    frm.fields["environments"][0].value = "test"
    res = frm.submit(expect_errors=True)
    assert res.status_code == 200
    assert res.context["adminform"].form.errors == {
        "event": ["This field is required."],
    }
    # add missing fields
    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["name"] = "Not2"
    frm["event"].force_value(notification.event.pk)
    frm.fields["environments"][0].value = "test"
    res = frm.submit(expect_errors=True)
    assert res.status_code == 200
    assert res.context["adminform"].form.errors == {
        "environments": ["One or more values are not available in the project"]
    }

    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["name"] = "Not2"
    frm["event"].force_value(notification.event.pk)
    res = frm.submit().follow()
    frm = res.forms["notification_form"]
    frm["distribution"].force_value(notification.distribution.pk)
    frm.fields["environments"][0].value = "development"
    res = frm.submit()
    assert res.status_code == 302


def test_add_dynamic(app: "DjangoTestApp", notification: "Notification") -> None:
    url = reverse("admin:bitcaster_notification_add")
    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["name"] = "Not2"
    frm["event"].force_value(notification.event.pk)
    frm.fields["environments"][0].value = "development"
    res = frm.submit()
    assert res.status_code == 302, res.context["adminform"].form.errors
    res = res.follow()
    assert not res.context["original"].active
    frm = res.forms["notification_form"]
    frm["active"] = True
    frm["policy"] = FILTERING_DYNAMIC
    frm["recipients_filter"] = json.dumps({"include": [], "exclude": []})
    res = frm.submit()
    assert res.status_code == 302, res.context["adminform"].form.errors


def test_add_external_filtering(app: "DjangoTestApp", notification: "Notification") -> None:
    url = reverse("admin:bitcaster_notification_add")
    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["name"] = "Not2"
    frm["event"].force_value(notification.event.pk)
    frm.fields["environments"][0].value = "development"
    res = frm.submit()
    assert res.status_code == 302, res.context["adminform"].form.errors
    res = res.follow()
    assert not res.context["original"].active
    frm = res.forms["notification_form"]
    frm["active"] = True
    frm["policy"] = FILTERING_EXTERNAL

    res = frm.submit()
    assert res.status_code == 302, res.context["adminform"].form.errors


def test_add_flag_compatibility(app: "DjangoTestApp", notification: "Notification") -> None:
    url = reverse("admin:bitcaster_notification_change", args=[notification.pk])
    res = app.get(url)
    frm = res.forms["notification_form"]
    frm["name"] = "Not2"
    frm["policy"] = FILTERING_NONE
    frm["distribution"].force_value(None)
    res = frm.submit()
    assert_form_error(res, "distribution", "This field is required")


def test_toggle_active(app: "DjangoTestApp", notification: "Notification") -> None:
    url = reverse("admin:bitcaster_notification_changelist")
    res = app.get(url)
    frm = res.forms["changelist-form"]
    selected_users = []
    for i in range(len(res.pyquery("input[name=_selected_action]"))):
        frm.get("_selected_action", index=i).checked = True
        selected_users.append(frm.get("_selected_action", index=i).value)
    frm["action"] = "toggle_active"
    frm.submit()
    assert not Notification.objects.filter(active=True).exists()
