import uuid
from typing import TYPE_CHECKING, TypedDict
from unittest.mock import Mock

import pytest
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

from bitcaster.constants import Bitcaster, SystemEvent
from bitcaster.tasks import process_event

if TYPE_CHECKING:
    from bitcaster.models import (
        Address,
        Channel,
        Event,
        Notification,
        Occurrence,
        Validation,
    )

    Context = TypedDict(
        "Context",
        {
            "occurrence": Occurrence,
            "address": Address,
            "channel": Channel,
            "validations": list[Validation],
            "silent_event": Event,
        },
    )


@pytest.fixture
def context(admin_user) -> "Context":
    from testutils.factories import (
        ChannelFactory,
        EventFactory,
        MessageFactory,
        NotificationFactory,
        OccurrenceFactory,
        ValidationFactory,
    )

    ch: "Channel" = ChannelFactory(name="test", dispatcher=fqn(TDispatcher))
    v1: Validation = ValidationFactory(channel=ch)
    v2: Validation = ValidationFactory(channel=ch)
    no: Notification = NotificationFactory(event__channels=[ch], distribution__recipients=[v1, v2])
    MessageFactory(channel=ch, event=no.event, content="Message for {{ event.name }} on channel {{channel.name}}")

    Bitcaster.initialize(admin_user)
    occurrence = OccurrenceFactory(event=no.event)
    return {
        "occurrence": occurrence,
        "address": v1.address,
        "channel": ch,
        "validations": [v1, v2],
        "silent_event": EventFactory(application__name="External"),
    }


def test_process_event_single(context: "Context", messagebox):
    from testutils.factories import OccurrenceFactory

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
    assert occurrence.status == OccurrenceFactory._meta.model.Status.PROCESSED
    assert occurrence.data == {
        "delivered": [v1.id, v2.id],
        "recipients": [[v1.address.value, "test"], [v2.address.value, "test"]],
    }


def test_process_incomplete_event(context: "Context", messagebox):
    from testutils.factories import OccurrenceFactory

    occurrence = context["occurrence"]
    v1, v2 = context["validations"]

    context["occurrence"].data["delivered"] = [v1.id, v2.id]
    context["occurrence"].save()

    process_event(occurrence.pk)
    assert messagebox == []

    occurrence.refresh_from_db()
    assert occurrence.status == OccurrenceFactory._meta.model.Status.PROCESSED
    assert occurrence.data == {"delivered": [v1.id, v2.id]}


def test_process_event_partially(context: "Context", monkeypatch):
    from testutils.factories import OccurrenceFactory

    occurrence: Occurrence = context["occurrence"]

    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel",
        mocked_notify := Mock(side_effect=[None, Exception("This is raised after first call")]),
    )

    process_event(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.status == OccurrenceFactory._meta.model.Status.NEW
    assert mocked_notify.call_count == 2
    assert occurrence.data == {
        "delivered": [context["validations"][0].id],
        "recipients": [["test@examplec.com", "test"]],
    }


def test_process_event_resume(context: "Context", monkeypatch):
    from testutils.factories import OccurrenceFactory

    occurrence = context["occurrence"]
    v1, v2 = context["validations"]

    occurrence.data = {"delivered": [v1.id], "recipients": [[v1.address.value, "test"]]}
    occurrence.save()

    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", mocked_notify := Mock())

    process_event(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.status == OccurrenceFactory._meta.model.Status.PROCESSED
    assert mocked_notify.call_count == 1
    assert occurrence.data == {
        "delivered": [v1.id, v2.id],
        "recipients": [["test@examplec.com", "test"], ["test@examplec.com", v1.channel.name]],
    }


def test_silent_event(context: "Context", monkeypatch):
    from testutils.factories import OccurrenceFactory

    cid = uuid.uuid4()
    e = context["silent_event"]
    o = e.trigger({"key": "value"}, cid=cid)

    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", Mock())

    assert o.__class__.objects.system(correlation_id=cid).count() == 0

    process_event(o.pk)

    o.refresh_from_db()
    assert o.status == OccurrenceFactory._meta.model.Status.PROCESSED
    assert o.data == {}
    assert o.__class__.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value).count() == 1
    assert o.__class__.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value, correlation_id=cid).count() == 1


def test_attempts(context: "Context", monkeypatch):
    from testutils.factories import OccurrenceFactory

    o = OccurrenceFactory(attempts=0, status=OccurrenceFactory._meta.model.Status.PROCESSED)
    process_event(o.pk)

    o.refresh_from_db()
    assert o.status == OccurrenceFactory._meta.model.Status.PROCESSED
    assert o.data == {}
