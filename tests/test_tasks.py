from typing import TYPE_CHECKING, TypedDict
from unittest.mock import Mock

import pytest
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

from bitcaster.tasks import process_event

if TYPE_CHECKING:
    from bitcaster.models import Address, Channel, Notification, Occurrence, Validation

    Context = TypedDict(
        "Context",
        {"occurrence": Occurrence, "address": Address, "channel": Channel, "validations": list[Validation]},
    )


@pytest.fixture
def context(db) -> "Context":
    from testutils.factories import (
        ChannelFactory,
        MessageFactory,
        NotificationFactory,
        OccurenceFactory,
        ValidationFactory,
    )

    ch: "Channel" = ChannelFactory(name="test", dispatcher=fqn(TDispatcher))
    v1: Validation = ValidationFactory(channel=ch)
    v2: Validation = ValidationFactory(channel=ch)
    no: Notification = NotificationFactory(event__channels=[ch], distribution__recipients=[v1, v2])
    # event: "Event" = EventFactory(application=ch.application)
    # event.channels.add(ch)
    MessageFactory(channel=ch, event=no.event, content="Message for {{ event.name }} on channel {{channel.name}}")

    # subscription = SubscriptionFactory(validation__channel=ch, event=event)
    occurrence = OccurenceFactory(event=no.event)
    return {"occurrence": occurrence, "address": v1.address, "channel": ch, "validations": [v1, v2]}


def test_process_event_single(context: "Context", messagebox):
    occurrence = context["occurrence"]
    v1, v2 = context["validations"]

    addr = context["address"]
    event = occurrence.event
    ch = context["channel"]
    process_event(occurrence.pk)
    assert messagebox == [
        (addr.value, f"Message for {event.name} on channel {ch.name}"),
        (v2.address.value, f"Message for {event.name} on channel {ch.name}"),
    ]
    occurrence.refresh_from_db()
    assert occurrence.processed
    assert occurrence.status == {
        "delivered": [v1.id, v2.id],
        "recipients": [[v1.address.value, "test"], [v2.address.value, "test"]],
    }


def test_process_incomplete_event(context: "Context", messagebox):
    occurrence = context["occurrence"]
    v1, v2 = context["validations"]

    context["occurrence"].status["delivered"] = [v1.id, v2.id]
    context["occurrence"].save()

    process_event(occurrence.pk)
    assert messagebox == []

    occurrence.refresh_from_db()
    assert occurrence.processed
    assert occurrence.status == {"delivered": [v1.id, v2.id]}


def test_process_event_partially(context: "Context", monkeypatch):
    occurrence: Occurrence = context["occurrence"]

    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel",
        mocked_notify := Mock(side_effect=[None, Exception("This is raised after first call")]),
    )

    process_event(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.processed is False
    assert mocked_notify.call_count == 2
    assert occurrence.status == {
        "delivered": [context["validations"][0].id],
        "recipients": [["test@examplec.com", "test"]],
    }


def test_process_event_resume(context: "Context", monkeypatch):

    occurrence = context["occurrence"]
    v1, v2 = context["validations"]

    occurrence.status = {"delivered": [v1.id], "recipients": [[v1.address.value, "test"]]}
    occurrence.save()

    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", mocked_notify := Mock())

    process_event(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.processed
    assert mocked_notify.call_count == 1
    assert occurrence.status == {
        "delivered": [v1.id, v2.id],
        "recipients": [["test@examplec.com", "test"], ["test@examplec.com", v1.channel.name]],
    }
