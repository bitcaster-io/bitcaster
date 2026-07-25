from typing import TYPE_CHECKING

import pytest
from testutils.factories.user import UserFactory
from testutils.perms import user_grant_permissions

from django.urls import reverse

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

pytestmark = [pytest.mark.admin, pytest.mark.django_db]


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    admin_user = UserFactory(username="staff")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_members_menu_visible_with_permission(app: "DjangoTestApp") -> None:
    with user_grant_permissions(app._user, ["bitcaster.view_member"]):
        res = app.get(reverse("admin:index"))
    assert "Members" in res


def test_members_menu_hidden_without_permission(app: "DjangoTestApp") -> None:
    res = app.get(reverse("admin:index"))
    assert "Members" not in res
