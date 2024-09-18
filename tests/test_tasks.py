import uuid
from typing import TYPE_CHECKING, Any, Tuple, TypedDict
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch
from strategy_field.utils import fqn
from testutils.dispatcher import XDispatcher

from bitcaster.constants import Bitcaster, SystemEvent
from bitcaster.tasks import (
    monitor_run,
    process_occurrence,
    purge_occurrences,
    schedule_occurrences,
)

if TYPE_CHECKING:
    from bitcaster.models import (
        Address,
        Assignment,
        Channel,
        Event,
        Notification,
        Occurrence,
        User,
    )

    Context = TypedDict(
        "Context",
        {
            "occurrence": Occurrence,
            # "silent_occurrence": Occurrence,
            "address": Address,
            "channel": Channel,
            "assignments": list[Assignment],
            "silent_event": Event,
        },
    )


@pytest.fixture
def setup(admin_user: "User") -> "Context":
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        EventFactory,
        MessageFactory,
        NotificationFactory,
        OccurrenceFactory,
    )

    ch: "Channel" = ChannelFactory(name="test", dispatcher=fqn(XDispatcher))
    v1: Assignment = AssignmentFactory(channel=ch, address__value="test1@example.com")
    v2: Assignment = AssignmentFactory(channel=ch, address__value="test2@example.com")
    no: Notification = NotificationFactory(event__channels=[ch], distribution__recipients=[v1, v2])
    MessageFactory(channel=ch, event=no.event, content="Message for {{ event.name }} on channel {{channel.name}}")

    Bitcaster.initialize(admin_user)

    o = OccurrenceFactory(event=no.event, attempts=3)
    return {
        "occurrence": o,
        "address": v1.address,
        "channel": ch,
        "assignments": [v1, v2],
        "silent_event": EventFactory(application__name="External"),
    }


@pytest.mark.django_db(transaction=True)
def test_process_event_single(setup: "Context", messagebox: list[Tuple[str, str]]) -> None:
    from bitcaster.models import Occurrence

    v1: Assignment = setup["assignments"][0]
    v2: Assignment = setup["assignments"][1]
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


def test_process_incomplete_event(setup: "Context", messagebox: list[Tuple[str, str]]) -> None:
    from bitcaster.models import Occurrence

    occurrence = setup["occurrence"]
    v1, v2 = setup["assignments"]

    setup["occurrence"].data["delivered"] = [v1.id, v2.id]
    setup["occurrence"].data["recipients"] = []
    setup["occurrence"].save()

    process_occurrence(occurrence.pk)
    assert messagebox == []

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSED
    assert occurrence.data == {"delivered": [v1.id, v2.id], "recipients": []}


@pytest.mark.django_db(transaction=True)
def test_process_event_partially(setup: "Context", monkeypatch: MonkeyPatch) -> None:
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
        "delivered": [setup["assignments"][0].id],
        "recipients": [["test1@example.com", "test"]],
    }


def test_process_event_resume(setup: "Context", monkeypatch: MonkeyPatch) -> None:
    from bitcaster.models import Occurrence

    v1: Assignment = setup["assignments"][0]
    v2: Assignment = setup["assignments"][1]
    occurrence = setup["occurrence"]

    occurrence.data = {"delivered": [v1.id], "recipients": [(v1.address.value, "test")]}
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


def test_silent_event(setup: "Context", monkeypatch: MonkeyPatch, system_objects: Any) -> None:
    from bitcaster.models import Occurrence

    cid = uuid.uuid4()
    e = setup["silent_event"]
    o = e.trigger(context={"key": "value"}, cid=cid)
    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", Mock())

    assert Occurrence.objects.system(correlation_id=cid).count() == 0
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.PROCESSED
    assert o.data == {}
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value).count() == 1
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value, correlation_id=cid).count() == 1


def test_attempts(setup: "Context", monkeypatch: MonkeyPatch) -> None:
    from testutils.factories import OccurrenceFactory

    from bitcaster.models import Occurrence

    o = OccurrenceFactory(attempts=0, status=Occurrence.Status.PROCESSED)
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.PROCESSED
    assert o.data == {}


def test_retry(setup: "Context", monkeypatch: MonkeyPatch, system_objects: Any) -> None:
    from bitcaster.models import Occurrence

    o = setup["occurrence"]
    v1 = setup["assignments"][0]

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


def test_error(setup: "Context", system_objects: Any) -> None:
    from testutils.factories import OccurrenceFactory

    from bitcaster.models import Occurrence

    o = OccurrenceFactory(attempts=0, status=Occurrence.Status.NEW)
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.FAILED
    assert o.data == {}


def test_processed(setup: "Context", monkeypatch: MonkeyPatch, system_objects: Any) -> None:
    from testutils.factories import OccurrenceFactory

    from bitcaster.models import Occurrence

    monkeypatch.setattr("bitcaster.models.occurrence.Occurrence.process", mocked_notify := Mock())

    o = OccurrenceFactory(status=Occurrence.Status.PROCESSED)
    process_occurrence(o.pk)
    assert mocked_notify.call_count == 0


@pytest.fixture(scope="session")
def celery_config() -> dict[str, str]:
    return {"broker_url": "memory://"}


# @pytest.mark.celery()
# @pytest.mark.skipif(os.getenv("GITLAB_CI") is not None, reason="Do not run on GitLab CI")
# def test_live(db, setup: "Context", monkeypatch, system_objects, celery_app, celery_worker):
#     o = setup["occurrence"]
#     assert process_occurrence.delay(o.pk).get(timeout=10) == 2


@pytest.mark.django_db(transaction=True)
def test_schedule_occurrences(setup: "Context", monkeypatch: MonkeyPatch) -> None:
    from bitcaster.models import Occurrence

    monkeypatch.setattr("bitcaster.models.occurrence.Occurrence.process", mocked_notify := Mock(return_value=True))

    schedule_occurrences()

    o: Occurrence = setup["occurrence"]
    o.refresh_from_db()
    assert mocked_notify.call_count == 1
    assert o.status == Occurrence.Status.PROCESSED


@pytest.mark.django_db(transaction=True)
def test_process_silent(setup: "Context", monkeypatch: MonkeyPatch) -> None:
    from testutils.factories import OccurrenceFactory

    from bitcaster.models import Event, Occurrence

    monkeypatch.setattr("bitcaster.models.occurrence.Occurrence.process", mocked_notify := Mock())

    silent_event = Event.objects.get(name=SystemEvent.OCCURRENCE_SILENCE.value)
    o = OccurrenceFactory(status=Occurrence.Status.NEW, event=silent_event)

    assert Occurrence.objects.filter(event=silent_event).count() == 1
    process_occurrence(o.pk)
    assert Occurrence.objects.filter(event=silent_event).count() == 1
    assert mocked_notify.call_count == 1


def test_purge_occurrences(
    purgeable_occurrences: list["Occurrence"], non_purgeable_occurrences: list["Occurrence"]
) -> None:
    from bitcaster.models import Occurrence

    assert Occurrence.objects.count() == len(purgeable_occurrences) + len(non_purgeable_occurrences)  # Sanity check

    purge_occurrences()

    assert Occurrence.objects.count() == len(non_purgeable_occurrences)
    assert Occurrence.objects.filter(pk__in=[o.pk for o in purgeable_occurrences]).count() == 0
    assert Occurrence.objects.filter(pk__in=[o.pk for o in non_purgeable_occurrences]).count() == len(
        non_purgeable_occurrences
    )


def test_monitor_run(system_user: "User") -> None:
    from testutils.factories.monitor import MonitorFactory

    monitor = MonitorFactory()
    monitor_run(monitor.pk)
