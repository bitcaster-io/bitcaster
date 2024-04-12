from typing import TYPE_CHECKING, TypedDict

from _pytest.fixtures import fixture
from strategy_field.utils import fqn
from testutils.factories import AddressFactory

from testutils.dispatcher import MESSAGES, TestDispatcher

if TYPE_CHECKING:
    from bitcaster.models import Address, ApiKey, Application, Channel, Event, Message, Subscription, User

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


@fixture
def context(db) -> "Context":
    from testutils.factories import (
        ApiKeyFactory,
        ApplicationFactory,
        ChannelFactory,
        EventFactory,
        MessageFactory,
        SubscriptionFactory,
    )

    app: "Application" = ApplicationFactory(name="Application-000")
    ch = ChannelFactory(organization=app.project.organization, name="test", dispatcher=fqn(TestDispatcher))
    evt = EventFactory(application=app)
    msg = MessageFactory(channel=ch, event=evt, content="Message for {{ event.name }} on channel {{channel.name}}")

    key = ApiKeyFactory(application=app)
    user: "User" = key.user

    addr = AddressFactory(user=user, channel=ch)
    sub = SubscriptionFactory(address=addr, event=evt, channels=[ch])

    return {"app": app, "event": evt, "key": key, "channel": ch, "subscription": sub, "message": msg, "address": addr}


def test_trigger(context: "Context"):
    addr: Address = context["address"]
    event: Event = context["event"]
    ch: Channel = context["channel"]
    event.trigger({})

    assert MESSAGES == [(addr.value, f"Message for {event.name} on channel {ch.name}")]
