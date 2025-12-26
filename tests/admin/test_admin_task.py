from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from strategy_field.utils import fqn

from bitcaster.runner.tasks import scan_occurrences

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import User


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
