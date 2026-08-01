from typing import TYPE_CHECKING, TypedDict

import pytest

from django.urls import reverse

from bitcaster.models import Subscription

if TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from django_webtest.pytest_plugin import MixinWithInstanceVariables

    from bitcaster.models import User

    Context = TypedDict("Context", {"subscription": Subscription})


@pytest.fixture
def app(django_app_factory: "MixinWithInstanceVariables", admin_user: "User") -> "DjangoTestApp":
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context(system_objects) -> "Context":
    from testutils.factories import (
        AddressFactory,
        AssignmentFactory,
        ChannelFactory,
        MemberFactory,
        MessageTemplateFactory,
        NotificationFactory,
        SubscriptionFactory,
    )

    from bitcaster.models import Organization

    org: "Organization" = Organization.objects.local().first()
    member = MemberFactory(organization=org)
    addr = AddressFactory(user=member, value=member.email)
    ch = ChannelFactory(organization=org)
    assignment = AssignmentFactory(address=addr, channel=ch)
    notification = NotificationFactory(event__channels=[ch], event__application__project__organization=org)
    MessageTemplateFactory(channel=ch, event=notification.event)
    subscription = SubscriptionFactory(notification=notification, assignment=assignment)
    return {"subscription": subscription}


def test_changelist(app: "DjangoTestApp", context: "Context") -> None:
    url = reverse("admin:bitcaster_subscription_changelist")
    res = app.get(url)
    assert res.status_code == 200
    assert str(context["subscription"].pk) in res


def test_change(app: "DjangoTestApp", context: "Context") -> None:
    subscription = context["subscription"]
    url = reverse("admin:bitcaster_subscription_change", args=[subscription.pk])
    res = app.get(url)
    assert res.status_code == 200


def test_change_initial_data(app: "DjangoTestApp", context: "Context") -> None:
    notification = context["subscription"].notification
    url = reverse("admin:bitcaster_subscription_add")
    res = app.get(f"{url}?notification={notification.pk}")
    assert res.status_code == 200
    frm = res.forms["subscription_form"]
    assert frm["notification"].value == str(notification.pk)


def test_changelist_search(app: "DjangoTestApp", context: "Context") -> None:
    url = reverse("admin:bitcaster_subscription_changelist")
    res = app.get(f"{url}?q={context['subscription'].assignment.address.value}")
    assert res.status_code == 200
    assert str(context["subscription"].pk) in res


def test_changelist_filter_user(app: "DjangoTestApp", context: "Context") -> None:
    subscription = context["subscription"]
    url = reverse("admin:bitcaster_subscription_changelist")
    res = app.get(f"{url}?assignment__address__user={subscription.assignment.address.user.pk}")
    assert res.status_code == 200
    assert str(subscription.pk) in res


def test_toggle_active(app: "DjangoTestApp", context: "Context") -> None:
    from testutils.factories import SubscriptionFactory

    SubscriptionFactory(notification=context["subscription"].notification)
    url = reverse("admin:bitcaster_subscription_changelist")
    res = app.get(url)
    frm = res.forms["changelist-form"]
    selected = []
    for i in range(len(res.pyquery("input[name=_selected_action]"))):
        frm.get("_selected_action", index=i).checked = True
        selected.append(frm.get("_selected_action", index=i).value)
    frm["action"] = "toggle_active"
    frm.submit()
    assert not Subscription.objects.filter(pk__in=selected, active=True).exists()
