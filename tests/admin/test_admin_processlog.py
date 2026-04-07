from typing import TYPE_CHECKING, Any

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import Application, ProcessLogEntry


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", db: Any) -> "DjangoTestApp":
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_changelist(app: "DjangoTestApp", processlogentry: "ProcessLogEntry", bitcaster: "Application") -> None:
    url = reverse("admin:bitcaster_processlogentry_changelist")
    res = app.get(url)
    assert res.status_code == 200


def test_change(app: "DjangoTestApp", processlogentry: "ProcessLogEntry", bitcaster: "Application") -> None:
    url = reverse("admin:bitcaster_processlogentry_change", args=[processlogentry.pk])
    res = app.get(url)
    res = res.click("Close")
    assert res.status_code == 200


def test_changelist_filter(app: "DjangoTestApp", processlogentry: "ProcessLogEntry", bitcaster: "Application") -> None:
    url = reverse("admin:bitcaster_processlogentry_changelist")
    res = app.get(url)
    res = res.click("monitor_check", href=r"\?task_func=bitcaster.runner.tasks.monitor_check")
    assert res.status_code == 200
