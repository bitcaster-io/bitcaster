from typing import TYPE_CHECKING, TypedDict

import pytest
from pytest_django import DjangoAssertNumQueries
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

if TYPE_CHECKING:
    from bitcaster.models import (
        Address,
        ApiKey,
        Application,
        Channel,
        Event,
        Message,
        Subscription,
        User,
    )

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "event": Event,
            "key": ApiKey,
            "channel": Channel,
            "subscription1": Subscription,
            "subscription2": Subscription,
            "message": Message,
            "address": Address,
        },
    )


@pytest.fixture
def context(db) -> "Context":
    from testutils.factories import (
        AddressFactory,
        ApiKeyFactory,
        ApplicationFactory,
        ChannelFactory,
        EventFactory,
        MessageFactory,
        SubscriptionFactory,
        ValidationFactory,
    )

    app: "Application" = ApplicationFactory(name="Application-000")
    ch = ChannelFactory(organization=app.project.organization, name="test", dispatcher=fqn(TDispatcher))
    evt = EventFactory(application=app)
    msg = MessageFactory(channel=ch, event=evt, content="Message for {{ event.name }} on channel {{channel.name}}")

    key: "ApiKey" = ApiKeyFactory(application=app)
    user: "User" = key.user

    addr: Address = AddressFactory(value="addr1@example.com", user=user)
    v = ValidationFactory(address=addr, channel=ch)
    sub1 = SubscriptionFactory(validation=v, event=evt)
    sub2 = SubscriptionFactory(event=evt, validation__channel=ch, validation__address__value="addr2@example.com")

    return {
        "app": app,
        "event": evt,
        "key": key,
        "channel": ch,
        "subscription1": sub1,
        "subscription2": sub2,
        "message": msg,
        "address": addr,
    }


def test_trigger(context: "Context", messagebox, django_assert_num_queries: "DjangoAssertNumQueries"):
    event: Event = context["event"]
    sub1: Subscription = context["subscription1"]
    sub2: Subscription = context["subscription2"]
    ch: Channel = context["channel"]
    o = event.trigger({})
    with django_assert_num_queries(10) as captured:
        o.process()
    msgs_queries = [q for q in captured if q["sql"].startswith('SELECT "bitcaster_message"')]
    assert len(msgs_queries) == 1, "get_message() cache is not working"

    assert messagebox == [
        (sub1.validation.address.value, f"Message for {event.name} on channel {ch.name}"),
        (sub2.validation.address.value, f"Message for {event.name} on channel {ch.name}"),
    ]
    o.refresh_from_db()
    assert o.status == {
        "delivered": [sub1.pk, sub2.pk],
        "recipients": [
            [sub1.validation.address.value, sub1.validation.channel.name],
            [sub2.validation.address.value, sub2.validation.channel.name],
        ],
    }
