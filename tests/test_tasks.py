import os
import uuid
from typing import TYPE_CHECKING, TypedDict
from unittest.mock import Mock

import pytest
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

from bitcaster.constants import Bitcaster, SystemEvent
from bitcaster.tasks import process_occurrence

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
def setup(admin_user) -> "Context":
    from testutils.factories import (
        ChannelFactory,
        EventFactory,
        MessageFactory,
        NotificationFactory,
        OccurrenceFactory,
        ValidationFactory,
    )

    ch: "Channel" = ChannelFactory(name="test", dispatcher=fqn(TDispatcher))
    v1: Validation = ValidationFactory(channel=ch, address__value="test1@example.com")
    v2: Validation = ValidationFactory(channel=ch, address__value="test2@example.com")
    no: Notification = NotificationFactory(event__channels=[ch], distribution__recipients=[v1, v2])
    MessageFactory(channel=ch, event=no.event, content="Message for {{ event.name }} on channel {{channel.name}}")

    Bitcaster.initialize(admin_user)
    o = OccurrenceFactory(event=no.event, attempts=3)
    return {
        "occurrence": o,
        "address": v1.address,
        "channel": ch,
        "validations": [v1, v2],
        "silent_event": EventFactory(application__name="External"),
    }


def test_process_event_single(setup: "Context", messagebox):
    from bitcaster.models import Occurrence

    v1: Validation = setup["validations"][0]
    v2: Validation = setup["validations"][1]
    occurrence = setup["occurrence"]

    addr = setup["address"]
    event = occurrence.event
    ch = setup["channel"]
    process_occurrence(occurrence.pk)
    assert messagebox == [
        (addr.value, f"Message for {event.name} on channel {ch.name}"),
        (v2.address.value, f"Message for {event.name} on channel {ch.name}"),
    ]
    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSED
    assert occurrence.data == {
        "delivered": [v1.id, v2.id],
        "recipients": [[v1.address.value, "test"], [v2.address.value, "test"]],
    }


def test_process_incomplete_event(setup: "Context", messagebox):
    from bitcaster.models import Occurrence

    occurrence = setup["occurrence"]
    v1, v2 = setup["validations"]

    setup["occurrence"].data["delivered"] = [v1.id, v2.id]
    setup["occurrence"].save()

    process_occurrence(occurrence.pk)
    assert messagebox == []

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSED
    assert occurrence.data == {"delivered": [v1.id, v2.id]}


def test_process_event_partially(setup: "Context", monkeypatch):
    from bitcaster.models import Occurrence

    occurrence: Occurrence = setup["occurrence"]

    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel",
        mocked_notify := Mock(side_effect=[None, Exception("This is raised after first call")]),
    )

    process_occurrence(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.NEW
    assert mocked_notify.call_count == 2
    assert occurrence.data == {
        "delivered": [setup["validations"][0].id],
        "recipients": [["test1@example.com", "test"]],
    }


def test_process_event_resume(setup: "Context", monkeypatch):
    from bitcaster.models import Occurrence

    v1: Validation = setup["validations"][0]
    v2: Validation = setup["validations"][1]
    occurrence = setup["occurrence"]

    occurrence.data = {"delivered": [v1.id], "recipients": [[v1.address.value, "test"]]}
    occurrence.save()

    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", mocked_notify := Mock())

    process_occurrence(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSED
    assert mocked_notify.call_count == 1
    assert occurrence.data == {
        "delivered": [v1.id, v2.id],
        "recipients": [["test1@example.com", "test"], ["test2@example.com", v1.channel.name]],
    }


def test_silent_event(setup: "Context", monkeypatch, system_events):
    from bitcaster.models import Occurrence

    cid = uuid.uuid4()
    e = setup["silent_event"]
    o = e.trigger({"key": "value"}, cid=cid)
    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", Mock())

    assert Occurrence.objects.system(correlation_id=cid).count() == 0
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.PROCESSED
    assert o.data == {}
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value).count() == 1
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value, correlation_id=cid).count() == 1


def test_attempts(setup: "Context", monkeypatch):
    from testutils.factories import Occurrence, OccurrenceFactory

    o = OccurrenceFactory(attempts=0, status=Occurrence.Status.PROCESSED)
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.PROCESSED
    assert o.data == {}


def test_retry(setup: "Context", monkeypatch, system_events):
    from testutils.factories import Occurrence

    o = setup["occurrence"]
    v1 = setup["validations"][0]

    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel",
        mocked_notify := Mock(side_effect=[None, Exception("This is raised after first call")]),
    )
    for a in range(10):
        process_occurrence(o.pk)
    o.refresh_from_db()
    assert o.attempts == 0
    assert o.status == Occurrence.Status.FAILED
    assert mocked_notify.call_count == 4
    assert o.data == {"delivered": [v1.id], "recipients": [[v1.address.value, "test"]]}


def test_error(setup: "Context", system_events):
    from testutils.factories import Occurrence, OccurrenceFactory

    o = OccurrenceFactory(attempts=0, status=Occurrence.Status.NEW)
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.FAILED
    assert o.data == {}


def test_processed(setup: "Context", monkeypatch, system_events):
    from testutils.factories import Occurrence, OccurrenceFactory

    monkeypatch.setattr("bitcaster.models.occurrence.Occurrence.process", mocked_notify := Mock())

    o = OccurrenceFactory(status=Occurrence.Status.PROCESSED)
    process_occurrence(o.pk)
    assert mocked_notify.call_count == 0


@pytest.fixture(scope="session")
def celery_config():
    return {"broker_url": "memory://"}


@pytest.mark.celery()
@pytest.mark.skipif(os.getenv("GITLAB_CI") is not None, reason="Do not run on GitLab CI")
def test_live(db, setup: "Context", monkeypatch, system_events, celery_app, celery_worker):
    o = setup["occurrence"]
    assert process_occurrence.delay(o.pk).get(timeout=10) == 2
