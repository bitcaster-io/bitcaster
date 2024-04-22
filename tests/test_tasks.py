from typing import TYPE_CHECKING, TypedDict
from unittest.mock import Mock

import pytest
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

from bitcaster.tasks import process_event

if TYPE_CHECKING:
    from bitcaster.models import (
        Address,
        Channel,
        Event,
        Occurrence,
        Subscription,
        Validation,
    )

    Context = TypedDict(
        "Context",
        {"occurrence": Occurrence, "address": Address, "channel": Channel, "subscription": Subscription},
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
    subscription = SubscriptionFactory(validation__channel=ch, event=event)
    occurrence = OccurenceFactory(event=event)
    return {"occurrence": occurrence, "address": v.address, "channel": ch, "subscription": subscription}


def test_process_event_single(context: "Context", messagebox):
    occurrence = context["occurrence"]
    addr = context["address"]
    event = occurrence.event
    ch = context["channel"]
    process_event(occurrence.pk)
    assert messagebox == [(addr.value, f"Message for {event.name} on channel {ch.name}")]
    occurrence.refresh_from_db()
    assert occurrence.processed
    assert occurrence.status == {
        "delivered": [context["subscription"].id],
        "recipients": [["test@examplec.com", "test"]],
    }


def test_process_incomplete_event(context: "Context", messagebox):
    occurrence = context["occurrence"]

    context["occurrence"].status["delivered"] = [context["subscription"].id]
    context["occurrence"].save()

    process_event(occurrence.pk)
    assert messagebox == []
    occurrence.refresh_from_db()
    assert occurrence.processed
    assert occurrence.status == {"delivered": [context["subscription"].id]}


def test_process_event_partially(context: "Context", monkeypatch):
    from testutils.factories import ChannelFactory, SubscriptionFactory

    occurrence = context["occurrence"]

    SubscriptionFactory(validation__channel=ChannelFactory(), event=context["subscription"].event)

    monkeypatch.setattr(
        "bitcaster.models.subscription.Subscription.notify",
        mocked_notify := Mock(side_effect=[None, Exception("This is raised after first call")]),
    )

    process_event(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.processed is False
    assert mocked_notify.call_count == 2
    assert occurrence.status == {
        "delivered": [context["subscription"].id],
        "recipients": [["test@examplec.com", "test"]],
    }


def test_process_event_resume(context: "Context", monkeypatch):
    from testutils.factories import ChannelFactory, SubscriptionFactory

    occurrence = context["occurrence"]
    sub1 = context["subscription"]

    sub2 = SubscriptionFactory(validation__channel=ChannelFactory(), event=sub1.event)
    occurrence.status = {"delivered": [context["subscription"].id], "recipients": [["test@examplec.com", "test"]]}
    occurrence.save()

    monkeypatch.setattr("bitcaster.models.subscription.Subscription.notify", mocked_notify := Mock())

    process_event(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.processed
    assert mocked_notify.call_count == 1
    assert occurrence.status == {
        "delivered": [context["subscription"].id, sub2.id],
        "recipients": [["test@examplec.com", "test"], ["test@examplec.com", sub2.validation.channel.name]],
    }
