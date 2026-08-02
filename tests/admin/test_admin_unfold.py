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


ALL_MENU_ITEMS = [
    ("Occurrences", "bitcaster.view_occurrence"),
    ("Members", "bitcaster.view_member"),
    ("Stream", "bitcaster.view_logmessage"),
    ("Messages", "bitcaster.view_usermessage"),
    ("Attachments", "bitcaster.view_attachment"),
    ("Addresses", "bitcaster.view_address"),
    ("Distribution List", "bitcaster.view_distributionlist"),
    ("Events", "bitcaster.view_event"),
    ("Notifications", "bitcaster.view_notification"),
    ("Message Templates", "bitcaster.view_messagetemplate"),
    ("Channels", "bitcaster.view_channel"),
    ("Applications", "bitcaster.view_application"),
    ("Projects", "bitcaster.view_project"),
    ("Organization", "bitcaster.view_organization"),
    ("Users", "bitcaster.view_user"),
    ("Roles", "bitcaster.view_userrole"),
    ("Groups", "auth.view_group"),
    ("API Keys", "bitcaster.view_apikey"),
    ("System Log", "admin.view_logentry"),
    ("SSO Providers", "social.view_socialprovider"),
    ("Event Simulations", "bitcaster.view_eventsimulation"),
    ("Delivery Simulations", "bitcaster.view_deliverysimulation"),
]


@pytest.mark.parametrize(("menu_item", "permission"), ALL_MENU_ITEMS)
def test_menu_item_visible_with_permission(app: "DjangoTestApp", menu_item: str, permission: str) -> None:
    with user_grant_permissions(app._user, [permission]):
        res = app.get(reverse("admin:index"))
    assert menu_item in res


@pytest.mark.parametrize(("menu_item",), [(item[0],) for item in ALL_MENU_ITEMS])
def test_menu_item_hidden_without_permission(app: "DjangoTestApp", menu_item: str) -> None:
    res = app.get(reverse("admin:index"))
    assert menu_item not in res
