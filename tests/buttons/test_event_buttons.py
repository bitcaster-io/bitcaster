from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse

from bitcaster.models import Subscription

if TYPE_CHECKING:
    from bitcaster.models import Address, Application, Channel, Event

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "channel": Channel,
            "event": Event,
            "address": Address,
        },
    )


@pytest.fixture()
def app(django_app_factory, admin_user):
    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


@pytest.fixture
def context(django_app_factory, admin_user) -> "Context":
    from testutils.factories import AddressFactory, ChannelFactory, EventFactory

    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user

    channel = ChannelFactory()
    event = EventFactory()
    event.channels.add(channel)
    address = AddressFactory(user=admin_user)
    AddressFactory(user=admin_user)  # other_addr

    return {"app": django_app, "channel": channel, "event": event, "address": address}


def test_event_subscribe(context: "Context"):
    app = context["app"]
    url = reverse("admin:bitcaster_event_subscribe", args=[context["event"].pk])
    res = app.get(url)
    assert res.status_code == 200, res.location
    assert (form := res.forms.get("subscribe-form")), "Should have subscribe-form"
    form["form-0-address"] = context["address"].pk
    res = form.submit().follow()
    assert res.status_code == 200, res.location

    subscription = Subscription.objects.get(address=context["address"], event=context["event"])
    assert list(subscription.channels.all()) == [context["channel"]]
