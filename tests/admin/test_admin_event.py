from typing import List, TYPE_CHECKING, TypedDict

import pytest
from django.urls import reverse

if TYPE_CHECKING:
    from bitcaster.models import Address, Application, Channel, Event

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "channel": Channel,
            "channel2": Channel,
            "event": Event,
            "address": Address,
            "address2": Address,
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
    channel2 = ChannelFactory()
    event = EventFactory()
    event.channels.add(channel)
    event.channels.add(channel2)
    address = AddressFactory(user=admin_user)
    address2 = AddressFactory(user=admin_user)  # other_addr

    return {
        "app": django_app, "channel": channel, "channel2": channel2,
        "event": event, "address": address, "address2": address2
    }


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


@pytest.mark.parametrize(
    'num_sub, which, result',
    [
        pytest.param(0, None, [], id='none'),
        pytest.param(1, [0], [], id='one'),
        pytest.param(2, True, [], id='all'),
        pytest.param(2, [1], [0], id='specific'),
        pytest.param(2, [2], [], id='all-selected'),
    ]
)
def test_event_unsubscribe(app, context: "Context", num_sub: int, which: List[int], result: List[int]) -> None:
    from bitcaster.models import Validation, Subscription
    validations = [
        Validation.objects.create(address=context['address'], channel=context['channel']),
        Validation.objects.create(address=context['address2'], channel=context['channel2'])
    ]
    channels = [context['channel'], context['channel2']]

    # Creating subscriptions
    subscriptions = [
        Subscription.objects.create(validation=validations[i], event=context['event'])
        for i in range(num_sub)
    ]
    expected = [s.id for i, s in enumerate(subscriptions) if i in result]

    if which is None:
        # No unsubscription
        pass
    elif which is True:
        # unsubscribing all
        context['event'].unsubscribe(user=context['address'].user)
    else:
        # unsubscribing from channels in which
        context['event'].unsubscribe(
            user=context['address'].user,
            channel_ids=[c.id for i, c in enumerate(channels) if i in which]
        )
    remaining = list(Subscription.objects.values_list('id', flat=True))

    assert remaining == expected, "Should have deleted the subscriptions"
