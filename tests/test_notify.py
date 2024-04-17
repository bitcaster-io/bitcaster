from typing import TYPE_CHECKING, TypedDict

import pytest
from strategy_field.utils import fqn
from testutils.dispatcher import TestDispatcher

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
            "subscription": Subscription,
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
    ch = ChannelFactory(organization=app.project.organization, name="test", dispatcher=fqn(TestDispatcher))
    evt = EventFactory(application=app)
    msg = MessageFactory(channel=ch, event=evt, content="Message for {{ event.name }} on channel {{channel.name}}")

    key: "ApiKey" = ApiKeyFactory(application=app)
    user: "User" = key.user

    addr: Address = AddressFactory(user=user)
    v = ValidationFactory(address=addr, channel=ch)
    sub = SubscriptionFactory(validation=v, event=evt)

    return {"app": app, "event": evt, "key": key, "channel": ch, "subscription": sub, "message": msg, "address": addr}


def test_trigger(context: "Context", messagebox):
    addr: Address = context["address"]
    event: Event = context["event"]
    ch: Channel = context["channel"]
    o = event.trigger({})
    o.process()
    assert messagebox == [(addr.value, f"Message for {event.name} on channel {ch.name}")]
