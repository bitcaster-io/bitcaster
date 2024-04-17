from typing import TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse

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
    from testutils.factories import (
        AddressFactory,
        ChannelFactory,
        EventFactory
    )

    django_app = django_app_factory(csrf_checks=False)
    django_app.set_user(admin_user)
    django_app._user = admin_user

    channel = ChannelFactory()
    event = EventFactory()
    event.channels.add(channel)
    address = AddressFactory(user=admin_user)  # other_addr

    return {"app": django_app, "channel": channel, "event": event, "address": address}


def test_event_subscribe(app, context: "Context") -> None:
    url = reverse("admin:bitcaster_event_subscribe", args=[context["event"].pk])
    res = app.get(url)
    assert res.status_code == 200, res.location
    assert (form := res.forms.get("subscribe-form")), "Should have subscribe-form"
    form["form-0-address"] = context["address"].pk
    res = form.submit().follow()
    assert res.status_code == 200, res.location

    from bitcaster.models import Subscription

    assert Subscription.objects.filter(
        validation__address=context["address"], event=context["event"], validation__channel=context["channel"]).exists()


def test_event_unsubscribe(app, context: "Context") -> None:
    from bitcaster.models import Validation
    validation = Validation.objects.create(address=context['address'], channel=context['channel'])

    # Should just not raise error
    context['event'].unsubscribe(user=context['address'].user, channel_id=context['channel'].id)

    from bitcaster.models import Subscription
    Subscription.objects.create(validation=validation, event=context['event'])

    context['event'].unsubscribe(user=context['address'].user, channel_id=context['channel'].id)
    assert Subscription.objects.count() == 0, "Should have deleted the subscription"
