from typing import TYPE_CHECKING

import pytest
from django.urls import reverse

from bitcaster.models import User

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_toggle_superuser(app: "DjangoTestApp") -> None:
    url = reverse("admin:bitcaster_user_changelist")
    res = app.get(url)
    frm = res.forms["changelist-form"]
    selected_users = []
    for i in range(len(res.pyquery("input[name=_selected_action]"))):
        frm.get("_selected_action", index=i).checked = True
        selected_users.append(frm.get("_selected_action", index=i).value)
    frm["action"] = "toggle_superuser"
    frm.submit()
    assert not User.objects.filter(is_superuser=False).exists()


def test_toggle_staff(app: "DjangoTestApp") -> None:
    url = reverse("admin:bitcaster_user_changelist")
    res = app.get(url)
    frm = res.forms["changelist-form"]
    selected_users = []
    for i in range(len(res.pyquery("input[name=_selected_action]"))):
        frm.get("_selected_action", index=i).checked = True
        selected_users.append(frm.get("_selected_action", index=i).value)
    frm["action"] = "toggle_staff"
    frm.submit()
    assert not User.objects.filter(is_staff=False).exists()
