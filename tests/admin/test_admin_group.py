from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse

from bitcaster.auth.constants import DEFAULT_GROUP_NAME

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import Channel, Event, User

    Context = TypedDict(
        "Context",
        {
            "group1": Channel,
            "group2": Event,
        },
    )


@pytest.fixture()
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "Context":
    from testutils.factories import GroupFactory

    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user

    group1 = GroupFactory(name=DEFAULT_GROUP_NAME)
    group2 = GroupFactory()

    return {"group1": group1, "group2": group2}


def test_get_readonly_if_default(app: "DjangoTestApp", context: "Context") -> None:
    url = reverse("admin:auth_group_change", args=[context["group1"].pk])
    res = app.get(url)
    frm = res.forms["group_form"]
    assert "name" not in frm.fields


def test_get_readonly_fields(app: "DjangoTestApp", context: "Context") -> None:
    url = reverse("admin:auth_group_change", args=[context["group2"].pk])
    res = app.get(url)
    res.forms["group_form"]["name"] = "abc"
    res = res.forms["group_form"].submit()
    assert res.status_code == 302
