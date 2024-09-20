# mypy: disable-error-code="union-attr"
from typing import TYPE_CHECKING, Any

import pytest
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.contrib.messages import (  # type: ignore[attr-defined]
    SUCCESS,
    WARNING,
    Message,
)
from django.db.models.options import Options
from django.http import HttpRequest
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils.safestring import SafeString
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from pytest_factoryboy import register
from strategy_field.utils import fqn
from testutils.factories import (
    ChannelFactory,
    OrganizationFactory,
    ProjectFactory,
    UserFactory,
)

from bitcaster.agents import AgentFileSystem
from bitcaster.models import Event, Monitor
from bitcaster.state import state

if TYPE_CHECKING:
    from webtest.forms import Form as WebTestForm
    from webtest.response import TestResponse

register(UserFactory)
register(OrganizationFactory)
register(ChannelFactory, "channel")
register(ProjectFactory, "project")


@pytest.fixture()
def app(django_app_factory: MixinWithInstanceVariables, rf: RequestFactory) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    request: HttpRequest = rf.get("/")
    request.user = admin_user

    with state.configure(request=request):
        yield django_app


@pytest.fixture()
def monitor(db: Any) -> Monitor:
    from testutils.factories.monitor import MonitorFactory, PeriodicTaskFactory

    return MonitorFactory(
        agent=fqn(AgentFileSystem),
        config={
            "path": ".",
        },
        schedule=PeriodicTaskFactory(interval=None),
        data={},
    )


def test_add(app: DjangoTestApp, event: "Event") -> None:
    url = reverse("admin:bitcaster_monitor_add")
    res = app.get(url)
    res.forms["monitor_form"]["name"] = "Monitor-1"
    res.forms["monitor_form"]["event"].force_value(event.pk)
    res.forms["monitor_form"]["agent"] = fqn(AgentFileSystem)
    res = res.forms["monitor_form"].submit()
    assert res.status_code == 302
    # configure
    res = res.follow()
    monitor: Monitor = res.context["original"]
    res.forms["config-form"]["path"] = "tests"
    res.forms["config-form"]["recursive"] = True
    res.forms["config-form"]["add"] = True
    res = res.forms["config-form"].submit()
    assert res.status_code == 302
    # schedule
    res = res.follow()
    res = res.forms["action-form"].submit()
    assert res.status_code == 302
    assert res.location == monitor.get_admin_change()


def test_change(app: DjangoTestApp, monitor: Monitor) -> None:
    url = reverse(admin_urlname(Monitor._meta, SafeString("change")), args=[monitor.pk])
    res = app.get(url)
    res = res.forms["monitor_form"].submit()
    assert res.status_code == 302


def test_configure(app: DjangoTestApp, monitor: "Monitor") -> None:
    opts: Options[Monitor] = Monitor._meta
    url = reverse(admin_urlname(opts, SafeString("configure")), args=[monitor.pk])
    res = app.get(url)
    assert res.status_code == 200

    res = app.post(url, {"path": ""})
    assert res.status_code == 200

    res = app.post(url, {"path": "/"})
    assert res.status_code == 302


def test_schedule(app: DjangoTestApp, monitor: "Monitor") -> None:
    url = reverse("admin:bitcaster_monitor_change", args=[monitor.pk])
    res: "TestResponse" = app.get(url)
    res = res.click("Schedule")
    frm: "WebTestForm" = res.forms["action-form"]
    frm["crontab"] = ""
    res = frm.submit()
    assert res.status_code == 200
    res.forms["action-form"]["crontab"] = monitor.schedule.crontab.pk
    res = res.forms["action-form"].submit()
    assert res.status_code == 302


def test_monitor_test(app: DjangoTestApp, monitor: "Monitor") -> None:
    msg: Message

    url = reverse("admin:bitcaster_monitor_test", args=[monitor.pk])
    assert monitor.data == {}
    res = app.get(url)
    assert res.status_code == 200

    res = app.post(url)
    assert res.status_code == 200
    assert len(res.context["messages"]) == 1
    msg = list(res.context["messages"])[0]
    assert msg.level == SUCCESS
    assert msg.message == "Success. No changes detected"

    monitor.agent.check()
    monitor.data["entries"] = {}
    monitor.save()
    res = app.post(url)
    assert res.status_code == 200
    msg = list(res.context["messages"])[0]
    assert msg.level == WARNING, str(f"{msg.level}: {msg.message}")
    assert msg.message == "Success. Changes detected"
