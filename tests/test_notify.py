from typing import TYPE_CHECKING, TypedDict

from _pytest.fixtures import fixture
from strategy_field.utils import fqn

from bitcaster.dispatchers.test import MESSAGES, TestDispatcher
from testutils.factories import AddressFactory

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application, Channel, EventType, Message, Subscription, User, Address

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "event": EventType,
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
        EventTypeFactory,
        MessageFactory,
        SubscriptionFactory,
    )

    app = ApplicationFactory(name="Application-000")
    ch = ChannelFactory(organization=app.project.organization, name="test", dispatcher=fqn(TestDispatcher))
    evt = EventTypeFactory(application=app)
    msg = MessageFactory(channel=ch, event=evt, content="Message for {{ event.name }} on channel {{channel.name}}")

    key = ApiKeyFactory(application=app)
    user: "User" = key.user

    addr = AddressFactory(user=user, channel=ch)
    sub = SubscriptionFactory(user=user, event=evt, channels=[ch])

    return {"app": app, "event": evt, "key": key, "channel": ch, "subscription": sub, "message": msg, "address": addr}


def test_trigger(context: "Context"):
    addr: Address = context["address"]
    event: EventType = context["event"]
    ch: Channel = context["channel"]
    event.trigger({})

    assert MESSAGES == [(addr.value, f'Message for {event.name} on channel {ch.name}')]
