from typing import TYPE_CHECKING, TypedDict

import pytest
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

from bitcaster.tasks import process_event

if TYPE_CHECKING:
    from bitcaster.models import Address, Channel, Event, Occurrence, Validation

    Context = TypedDict(
        "Context",
        {
            "occurrence": Occurrence,
            "address": Address,
            "channel": Channel,
        },
    )


@pytest.fixture
def context(db) -> "Context":
    from testutils.factories import (
        ChannelFactory,
        EventFactory,
        MessageFactory,
        OccurenceFactory,
        SubscriptionFactory,
        ValidationFactory,
    )

    ch: "Channel" = ChannelFactory(name="test", dispatcher=fqn(TDispatcher))

    event: "Event" = EventFactory(application=ch.application)
    event.channels.add(ch)
    MessageFactory(channel=ch, event=event, content="Message for {{ event.name }} on channel {{channel.name}}")

    v: Validation = ValidationFactory(channel=ch)
    SubscriptionFactory(validation__channel=ch, event=event)
    occurrence = OccurenceFactory(event=event)
    return {"occurrence": occurrence, "address": v.address, "channel": ch}


def test_process_event(context: "Context", messagebox):
    occurrence = context["occurrence"]
    addr = context["address"]
    event = occurrence.event
    ch = context["channel"]
    process_event(occurrence.pk)
    assert messagebox == [(addr.value, f"Message for {event.name} on channel {ch.name}")]
