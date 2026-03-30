import json
from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from strategy_field.utils import fqn
from testutils.helpers import assert_form_error

from bitcaster.runner.tasks import scan_occurrences

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import Task, User


@pytest.fixture
def task() -> "Task":
    from testutils.factories import TaskFactory

    return TaskFactory()


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_task_add(app: "DjangoTestApp") -> None:
    url = reverse("admin:bitcaster_task_add")
    res = app.get(url)
    frm = res.forms["task_form"]
    frm["func"] = fqn(scan_occurrences)
    frm["name"] = "Scan Occurrences"
    res = frm.submit()
    assert res.status_code == 302, res.showbrowser()
    res = res.follow()
    new_task = res.context["original"]
    assert res.request.path == reverse("admin:bitcaster_task_change", args=[new_task.id])


@pytest.mark.parametrize("trigger, config", [("interval", {"minutes": 1}), ("cron", {"minute": 1})])
def test_task_change(app: "DjangoTestApp", trigger, config, task) -> None:
    url = reverse("admin:bitcaster_task_change", args=[task.id])
    res = app.get(url)
    frm = res.forms["task_form"]
    new_name = "New Task Name"
    frm["name"] = new_name
    frm["trigger"] = trigger
    frm["trigger_config"] = json.dumps(config)
    res = frm.submit()
    assert res.status_code == 302, res.showbrowser()
    task.refresh_from_db()
    assert task.name == new_name


@pytest.mark.parametrize("trigger, config", [("interval", {"a": 1}), ("cron", {"b": 1})])
def test_task_invalid_config(app: "DjangoTestApp", trigger, config, task) -> None:
    url = reverse("admin:bitcaster_task_change", args=[task.id])
    res = app.get(url)
    frm = res.forms["task_form"]
    new_name = "New Task Name"
    frm["name"] = new_name
    frm["trigger"] = trigger
    frm["trigger_config"] = json.dumps(config)
    res = frm.submit()
    assert res.status_code == 200
    assert_form_error(res, "trigger_config", "got an unexpected keyword", partial=True)


def test_task_change_invalid_trigger(app: "DjangoTestApp") -> None:
    from testutils.factories import TaskFactory

    task = TaskFactory(trigger="-", trigger_config={})  # Use factory directly
    url = reverse("admin:bitcaster_task_change", args=[task.id])
    res = app.get(url)
    frm = res.forms["task_form"]
    new_name = "New Task Name"
    frm["name"] = new_name
    frm["trigger"].force_value("")
    res = frm.submit()
    assert res.status_code == 200
    assert_form_error(res, "trigger", "This field is required.")
    assert_form_error(res, "trigger", "Please select a valid trigger")


def test_task_pause_resume(app: "DjangoTestApp", task) -> None:
    url = reverse("admin:bitcaster_task_change", args=[task.id])
    res = app.get(url)
    res = res.click("Resume").follow()
    assert res.status_code == 200
    res = res.click("Pause").follow()
    assert res.status_code == 200
