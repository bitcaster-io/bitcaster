from typing import TYPE_CHECKING, Any, TypedDict

import pytest
from django.urls import reverse
from django_webtest import DjangoTestApp
from django_webtest.pytest_plugin import MixinWithInstanceVariables
from testutils.helpers import assert_message

from bitcaster.constants import AddressType

if TYPE_CHECKING:
    from bitcaster.models import Address, Channel, DistributionList, Member, Notification, Organization

    Context = TypedDict(
        "Context",
        {
            "organization": Organization,
            "channel": Channel,
            "notification": Notification,
            "distributionlist": DistributionList,
            "members": list[Member],
        },
    )


@pytest.fixture
def app(django_app_factory: MixinWithInstanceVariables, db: Any) -> DjangoTestApp:
    from testutils.factories import SuperUserFactory

    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context(system_objects) -> "Context":
    from testutils.factories import (
        AddressFactory,
        AssignmentFactory,
        ChannelFactory,
        DistributionListFactory,
        MemberFactory,
        NotificationFactory,
        OrganizationFactory,
    )

    org: "Organization" = OrganizationFactory.create()
    ch: "Channel" = ChannelFactory.create(organization=org)
    members = [MemberFactory.create(organization=org), MemberFactory(organization=org)]
    addr = AddressFactory.create(user=members[0], value=members[0].email)
    distribution = DistributionListFactory.create(recipients=[AssignmentFactory.create(address=addr, channel=ch)])
    notification = NotificationFactory.create(id=1, distribution=distribution, event__channels=[ch])
    return {
        "organization": org,
        "channel": ch,
        "notification": notification,
        "distributionlist": distribution,
        "members": members,
    }


def test_add_and_redirect(app: DjangoTestApp) -> None:
    base_url = reverse("admin:bitcaster_address_add")
    url = f"{base_url}?next=www.bitcaster.io"
    res = app.post(url, {"user": -1})
    assert res.status_code == 200
    res = app.post(
        url,
        {"user": app._user.pk, "name": "address #1", "type": AddressType.EMAIL, "value": "me@bitcaster.io"},
    )
    assert res.status_code == 302
    assert res.location == "www.bitcaster.io"


@pytest.mark.parametrize(
    "value, t",
    [("user@email.com", AddressType.EMAIL), ("+12299088128", AddressType.PHONE), ("account", AddressType.ACCOUNT)],
)
def test_add_address_types(app: DjangoTestApp, value: str, t: AddressType) -> None:
    base_url = reverse("admin:bitcaster_address_add")
    url = f"{base_url}?next=www.bitcaster.io"
    res = app.post(url, {"user": app._user.pk, "name": "address #1", "value": value, "type": AddressType.GENERIC})
    assert res.status_code == 302
    assert res.location == "www.bitcaster.io"


def test_assign_to_channel_single(app: DjangoTestApp, address: "Address", channel: "Channel") -> None:
    url = reverse("admin:bitcaster_address_assign_to_channel_single", args=[address.pk])
    res = app.get(url).follow()
    assert_message(res, "Channel not found")

    res = app.get(f"{url}?ch={channel.pk}").follow()
    assert_message(res, "Channel successfully assigned")
    assert address.assignments.filter(channel=channel).exists()


def test_assign_to_channel(app: "DjangoTestApp", address: "Address", channel) -> None:
    url = reverse("admin:bitcaster_address_changelist")
    res = app.get(url)
    frm = res.forms["changelist-form"]
    selection = []
    for i in range(len(res.pyquery("input[name=_selected_action]"))):
        frm.get("_selected_action", index=i).checked = True
        selection.append(frm.get("_selected_action", index=i).value)
    frm["action"] = "assign_to_channel"
    res = frm.submit()
    res.forms["assign_form"]["channel"] = channel.pk
    res = res.forms["assign_form"].submit("apply")
    assert res.status_code == 302
    address.refresh_from_db()
    assert address.assignments.filter(channel=channel).exists()


@pytest.mark.parametrize("flt", ["dl=1", "dl=", "dl=invalid", "n=1", "n=", "n=invalid"])
def test_address_filtering(app: "DjangoTestApp", context: "Context", flt: str) -> None:
    url = reverse("admin:bitcaster_address_changelist")
    res = app.get(f"{url}?{flt}")
    assert res.status_code == 200


@pytest.mark.django_db
def test_address_distributionlist_filter(app: "DjangoTestApp", context: "Context") -> None:
    url = reverse("admin:bitcaster_address_changelist")
    distributionlist = context["distributionlist"]
    asm = distributionlist.recipients.first()
    member = context["members"][1]

    res = app.get(f"{url}?dl={distributionlist.pk}")
    assert asm.address.user.username in res
    assert member.username not in res
