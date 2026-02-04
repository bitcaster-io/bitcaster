from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse
from testutils.helpers import assert_form_error, assert_message, get_resource
from webtest import Upload

from bitcaster.admin.member import JsonUpdateMode2
from bitcaster.models import Assignment, Channel, DistributionList, Member, Organization, User

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    Context = TypedDict(
        "Context",
        {"organization": Organization, "members": list[Member]},
    )


@pytest.fixture
def context(system_objects) -> "Context":
    from testutils.factories import (
        AddressFactory,
        AssignmentFactory,
        ChannelFactory,
        MemberFactory,
        OrganizationFactory,
    )

    org: "Organization" = OrganizationFactory()
    ch: "Channel" = ChannelFactory(organization=org)
    members = [MemberFactory(organization=org), MemberFactory(organization=org)]
    addr = AddressFactory(user=members[0], value=members[0].email)
    AssignmentFactory(address=addr, channel=ch)
    return {
        "organization": org,
        "members": members,
    }


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


def test_member_add(app: "DjangoTestApp", context: "Context"):
    member = context["members"][0]
    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    res.forms["member_form"]["custom_fields"] = "{}"
    res = res.forms["member_form"].submit()
    assert res.status_code == 302, res.context["form"].errors


@pytest.mark.parametrize("value, expected", [("{", "Invalid JSON."), ("[]", "Must be a dictionary.")])
def test_member_check_custom_fields(app: "DjangoTestApp", value, expected) -> None:
    url = reverse("admin:bitcaster_member_add")
    res = app.get(url)
    res.forms["member_form"]["custom_fields"] = value
    res = res.forms["member_form"].submit("apply")
    assert res.status_code == 200
    assert_form_error(res, "custom_fields", expected)


def test_add_to_distributionlist(app: "DjangoTestApp", distributionlist: "DistributionList") -> None:
    from testutils.factories import AssignmentFactory

    AssignmentFactory.create_batch(5)
    url = reverse("admin:bitcaster_member_changelist")
    res = app.get(url)
    frm = res.forms["changelist-form"]
    selected_users = []
    for i in range(len(res.pyquery("input[name=_selected_action]"))):
        frm.get("_selected_action", index=i).checked = True
        selected_users.append(frm.get("_selected_action", index=i).value)
    frm["action"] = "add_to_distributionlist"
    res = frm.submit()
    frm = res.forms["action-form"]
    res = frm.submit("apply")
    assert res.status_code == 200

    frm = res.forms["action-form"]
    frm["dl"] = distributionlist.pk
    res = frm.submit("apply")
    assert res.status_code == 302, res.context["form"].errors
    assert distributionlist.recipients.count() == Assignment.objects.filter(address__user__in=selected_users).count()


@pytest.mark.parametrize("mode", [JsonUpdateMode2.MERGE, JsonUpdateMode2.REWRITE])
def test_update_custom_fields(app: "DjangoTestApp", context: "Context", mode) -> None:
    url = reverse("admin:bitcaster_member_changelist")
    res = app.get(url)
    frm = res.forms["changelist-form"]
    selected_users = []
    for i in range(len(res.pyquery("input[name=_selected_action]"))):
        frm.get("_selected_action", index=i).checked = True
        selected_users.append(frm.get("_selected_action", index=i).value)
    frm["action"] = "update_custom_fields"
    res = frm.submit()
    res.forms["action-form"]["custom_fields"] = '{"text": "abc"}'
    res.forms["action-form"]["mode"] = mode
    res = res.forms["action-form"].submit("apply").follow()
    assert_message(res, "Record successfully updated")


def test_import_members_ui(app: "DjangoTestApp", local_organization) -> None:
    url = reverse("admin:bitcaster_member_changelist")
    res = app.get(url)
    res = res.click("Import Members")
    res.forms["action-form"]["file"] = Upload(str(get_resource("data/members_mixed.csv").absolute()))
    res = res.forms["action-form"].submit("apply").follow()
    assert_message(res, "Record successfully imported 2/3")
