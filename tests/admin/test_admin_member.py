from typing import TYPE_CHECKING, Any, TypedDict

from webtest import Upload

import pytest
from testutils.factories import DistributionListFactory
from testutils.helpers import assert_form_error, assert_message, get_resource

from django.urls import reverse

from bitcaster.admin.member import JsonUpdateMode2
from bitcaster.models import Assignment, Channel, DistributionList, Member, Organization, User

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    Context = TypedDict(
        "Context",
        {"organization": Organization, "distributionlist": DistributionList, "members": list[Member]},
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

    org: "Organization" = OrganizationFactory.create()
    ch: "Channel" = ChannelFactory.create(organization=org)
    members = [MemberFactory.create(organization=org), MemberFactory(organization=org)]
    addr = AddressFactory(user=members[0], value=members[0].email)
    return {
        "organization": org,
        "distributionlist": DistributionListFactory.create(
            recipients=[AssignmentFactory.create(address=addr, channel=ch)]
        ),
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


def test_member_subscriptions_inline(app: "DjangoTestApp", context: "Context") -> None:
    from testutils.factories import (
        AddressFactory,
        AssignmentFactory,
        ChannelFactory,
        MessageTemplateFactory,
        NotificationFactory,
    )

    from bitcaster.models import Subscription

    member = context["members"][0]
    addr = AddressFactory(user=member, value=member.email)
    ch = ChannelFactory(organization=context["organization"])
    assignment = AssignmentFactory(address=addr, channel=ch)
    notification = NotificationFactory(event__channels=[ch])
    MessageTemplateFactory(channel=ch, event=notification.event)

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    form = res.forms["member_form"]
    params: dict[str, Any] = {
        name: [v for v in (f.value for f in fields) if v is not None]
        for name, fields in form.fields.items()
        if "__prefix__" not in name
    }
    params["custom_fields"] = "{}"
    params["bitcaster-subscription-TOTAL_FORMS"] = "1"
    params["bitcaster-subscription-INITIAL_FORMS"] = "0"
    params["bitcaster-subscription-0-notification"] = str(notification.pk)
    params["bitcaster-subscription-0-assignment"] = str(assignment.pk)
    params["bitcaster-subscription-0-active"] = "on"
    params["_save"] = "Save"
    res = app.post(url, params=params)
    assert res.status_code == 302, res
    assert Subscription.objects.filter(assignment=assignment, notification=notification).exists()


def test_member_subscriptions_inline_display(app: "DjangoTestApp", context: "Context") -> None:
    from testutils.factories import (
        AddressFactory,
        AssignmentFactory,
        ChannelFactory,
        MessageTemplateFactory,
        NotificationFactory,
        SubscriptionFactory,
    )

    member = context["members"][0]
    addr = AddressFactory(user=member, value=member.email)
    ch = ChannelFactory(organization=context["organization"])
    assignment = AssignmentFactory(address=addr, channel=ch)
    notification = NotificationFactory(event__channels=[ch])
    MessageTemplateFactory(channel=ch, event=notification.event)
    subscription = SubscriptionFactory(notification=notification, assignment=assignment)

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    assert str(subscription.pk) in res
    assert "bitcaster-subscription" in res


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


@pytest.mark.parametrize("mode", [JsonUpdateMode2.MERGE])
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


@pytest.mark.parametrize("flt", ["dl=1", "dl="])
def test_member_filtering(app: "DjangoTestApp", context: "Context", flt: str) -> None:
    url = reverse("admin:bitcaster_member_changelist")
    res = app.get(f"{url}?{flt}")
    assert res.status_code == 200


@pytest.mark.django_db
def test_member_distributionlist_filter(app: "DjangoTestApp", context: "Context") -> None:
    url = reverse("admin:bitcaster_member_changelist")
    distributionlist = context["distributionlist"]
    asm = distributionlist.recipients.first()
    member = context["members"][1]

    res = app.get(f"{url}?dl={distributionlist.pk}")
    assert asm.address.user.username in res
    assert member.username not in res


def test_assignment_inline_save(app: "DjangoTestApp", context: "Context"):
    from testutils.factories import AddressFactory, ChannelFactory

    member = context["members"][0]
    channel = ChannelFactory(organization=context["organization"])
    address = AddressFactory(user=member)

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    form = res.forms["member_form"]

    prefix = "bitcaster-assignment"
    form[f"{prefix}-TOTAL_FORMS"] = "1"
    form[f"{prefix}-0-address"] = address.pk
    form[f"{prefix}-0-channel"] = channel.pk

    res = form.submit().follow()
    assert res.status_code == 200
    assert Assignment.objects.filter(address=address, channel=channel).exists()


def test_assignment_inline_list(app: "DjangoTestApp", context: "Context"):
    from testutils.factories import AssignmentFactory

    member = context["members"][0]
    AssignmentFactory(address__user=member)

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    assert res.status_code == 200


def test_member_distribution_lists_assignment_shown(app: "DjangoTestApp", context: "Context"):
    member = context["members"][0]
    dl = context["distributionlist"]
    asm = dl.recipients.first()

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    assert res.status_code == 200
    rows = res.pyquery("#bitcaster-distributionlist-group tbody.form-group:not(.template)")
    assert len(rows) == 1
    assert res.pyquery("#id_bitcaster-distributionlist-0-dl option[selected]").val() == str(dl.pk)
    assert res.pyquery("#id_bitcaster-distributionlist-0-assignment option[selected]").val() == str(asm.pk)


def test_member_distribution_lists_multiple_assignments_single_row(app: "DjangoTestApp", context: "Context"):
    from testutils.factories import AddressFactory, AssignmentFactory

    member = context["members"][0]
    dl = context["distributionlist"]
    channel = dl.recipients.first().channel
    dl.recipients.add(AssignmentFactory(address=AddressFactory(user=member), channel=channel))

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    assert res.status_code == 200
    rows = res.pyquery("#bitcaster-distributionlist-group tbody.form-group:not(.template)")
    assert len(rows) == 1
    assert dl.name in res.text
    assert member.email in res.text


def test_member_distribution_lists_add(app: "DjangoTestApp", context: "Context"):
    from testutils.factories import DistributionListFactory

    member = context["members"][0]
    dl = DistributionListFactory.create(project=context["distributionlist"].project)
    asm = context["distributionlist"].recipients.first()

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    form = res.forms["member_form"]
    prefix = "bitcaster-distributionlist"
    form[f"{prefix}-1-dl"] = dl.pk
    form[f"{prefix}-1-assignment"] = asm.pk

    res = form.submit().follow()
    assert res.status_code == 200
    assert dl.recipients.filter(pk=asm.pk).exists()


def test_member_distribution_lists_add_any_assignment(app: "DjangoTestApp", context: "Context"):
    from testutils.factories import AddressFactory, AssignmentFactory, DistributionListFactory

    member = context["members"][0]
    dl = DistributionListFactory.create(project=context["distributionlist"].project)
    first = context["distributionlist"].recipients.first()
    second = AssignmentFactory(address=AddressFactory(user=member), channel=first.channel)

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    form = res.forms["member_form"]
    prefix = "bitcaster-distributionlist"
    form[f"{prefix}-1-dl"] = dl.pk
    form[f"{prefix}-1-assignment"] = second.pk

    res = form.submit().follow()
    assert res.status_code == 200
    assert list(dl.recipients.values_list("pk", flat=True)) == [second.pk]


def test_member_distribution_lists_add_no_address(app: "DjangoTestApp", context: "Context"):
    from testutils.factories import DistributionListFactory

    member = context["members"][1]
    dl = DistributionListFactory.create(project=context["distributionlist"].project)

    url = reverse("admin:bitcaster_member_change", args=[member.pk])
    res = app.get(url)
    form = res.forms["member_form"]
    prefix = "bitcaster-distributionlist"
    form[f"{prefix}-0-dl"] = dl.pk

    res = form.submit()
    assert res.status_code == 200
    assert "This field is required" in res.text
    assert not dl.recipients.exists()


def test_member_distribution_lists_form_without_assignment(app: "DjangoTestApp", context: "Context"):
    from bitcaster.admin.member import ListsForm

    member = context["members"][0]
    dl = context["distributionlist"]

    form = ListsForm(user=member, dl_initial=dl, assignment_initial=None)
    assert form.fields["dl"].disabled is True
    assert form.fields["dl"].initial == dl
    assert form.fields["assignment"].disabled is False
    assert form.fields["assignment"].initial is None


def test_member_distribution_lists_formset_save_new_empty():
    from types import SimpleNamespace

    from unfold.contrib.inlines.forms import nonrelated_inline_formset_factory

    from bitcaster.admin.member import ListsForm, ListsFormSet

    formset = nonrelated_inline_formset_factory(
        model=DistributionList,
        queryset=DistributionList.objects.none(),
        form=ListsForm,
        formset=ListsFormSet,
    )
    form = SimpleNamespace(cleaned_data={"dl": None, "assignment": None})
    assert formset().save_new(form) is None
