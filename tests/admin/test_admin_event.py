from typing import TYPE_CHECKING, TypedDict

import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.messages import SUCCESS, Message  # type: ignore[attr-defined]
from django.db.models.options import Options
from django.urls import reverse

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import Assignment, Channel, Event, Notification, User

    Context = TypedDict(
        "Context",
        {
            "channel": Channel,
            "event": Event,
            "assignment": Assignment,
        },
    )


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context(app: "DjangoTestApp") -> "Context":
    from testutils.factories import AssignmentFactory, NotificationFactory

    asm: "Assignment" = AssignmentFactory(address__user=app._user)
    n: "Notification" = NotificationFactory(distribution__recipients=[asm], event__channels=[asm.channel])

    return {
        "channel": asm.channel,
        "assignment": asm,
        "event": n.event,
    }


def test_trigger_event(app: "DjangoTestApp", context: "Context") -> None:
    event: Event = context["event"]
    opts: "Options[Event]" = event._meta
    url = reverse(admin_urlname(opts, "trigger_event"), args=[event.pk])  # type: ignore[arg-type]
    res = app.post(url, {})
    assert res.status_code == 200

    res = app.get(url)
    assert res.status_code == 200
    res.forms["test-form"]["assignment"] = context["assignment"].pk
    res = res.forms["test-form"].submit().follow()

    assert len(res.context["messages"]) == 1
    msg: Message = list(res.context["messages"])[0]
    assert msg.level == SUCCESS
