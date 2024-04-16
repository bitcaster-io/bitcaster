from typing import TYPE_CHECKING, TypedDict

from _pytest.fixtures import fixture
from strategy_field.utils import fqn
from testutils.dispatcher import MESSAGES, TestDispatcher
from testutils.factories.address import AddressFactory
from testutils.factories.channel import ChannelFactory
from testutils.factories.event import EventFactory
from testutils.factories.key import ApiKeyFactory
from testutils.factories.message import MessageFactory
from testutils.factories.org import ApplicationFactory
from testutils.factories.subscription import SubscriptionFactory
from testutils.factories.validation import ValidationFactory

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

    app: "Application" = ApplicationFactory(name="Application-000")
    ch = ChannelFactory(organization=app.project.organization, name="test", dispatcher=fqn(TestDispatcher))
    evt = EventFactory(application=app)
    msg = MessageFactory(channel=ch, event=evt, content="Message for {{ event.name }} on channel {{channel.name}}")

    key = ApiKeyFactory(application=app)
    user: "User" = key.user

    addr = AddressFactory(user=user, channel=ch)
    validation = ValidationFactory(address=addr, channel=ch)
    sub = SubscriptionFactory(validation=validation, event=evt, channels=[ch])

    return {"app": app, "event": evt, "key": key, "channel": ch, "subscription": sub, "message": msg, "address": addr}


def test_trigger(context: "Context"):
    addr: Address = context["address"]
    event: Event = context["event"]
    ch: Channel = context["channel"]
    o = event.trigger({})
    o.process()
    assert MESSAGES == [(addr.value, f"Message for {event.name} on channel {ch.name}")]
