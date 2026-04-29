import uuid
from typing import TYPE_CHECKING, Any, TypedDict
from unittest.mock import Mock, patch

import pytest
from strategy_field.utils import fqn
from testutils.dispatcher import XDispatcher
from testutils.factories import MonitorFactory
from testutils.perms import configure_model

from bitcaster.constants import SystemEvent, bitcaster
from bitcaster.dispatchers import UserMessageDispatcher
from bitcaster.models import Channel, Event, Monitor, Occurrence, UserMessage
from bitcaster.runner.tasks import (
    check_for_new_user_messages,
    delete_expired_user_messages,
    monitor_check,
    monitor_run,
    process_occurrence,
    purge_occurrences,
    scan_occurrences,
)

if TYPE_CHECKING:
    from bitcaster.models import (
        Address,
        Assignment,
        MessageTemplate,
        Notification,
        User,
    )

    Context = TypedDict(
        "Context",
        {
            "occurrence": Occurrence,
            "address": Address,
            "channel": Channel,
            "assignments": list[Assignment],
            "silent_event": Event,
            "notification": Notification,
            "message": MessageTemplate,
        },
    )


@pytest.fixture
def setup(admin_user: "User") -> "Context":
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        EventFactory,
        MessageTemplateFactory,
        NotificationFactory,
        OccurrenceFactory,
    )

    ch: "Channel" = ChannelFactory.create(name="test", dispatcher=fqn(XDispatcher))
    v1: Assignment = AssignmentFactory.create(channel=ch, address__value="test1@example.com")
    v2: Assignment = AssignmentFactory.create(channel=ch, address__value="test2@example.com")
    no: Notification = NotificationFactory.create(event__channels=[ch], distribution__recipients=[v1, v2])
    msg = MessageTemplateFactory.create(
        channel=ch, event=no.event, content="Message for {{ event.name }} on channel {{channel.name}}"
    )

    bitcaster.initialize(admin_user)

    o = OccurrenceFactory(event=no.event, attempts=3)
    return {
        "occurrence": o,
        "address": v1.address,
        "channel": ch,
        "message": msg,
        "assignments": [v1, v2],
        "notification": no,
        "silent_event": EventFactory.create(application__name="External"),
    }


@pytest.fixture
def monitor() -> "Monitor":
    return MonitorFactory.create()


@pytest.mark.django_db(transaction=True)
def test_process_event_single(setup: "Context") -> None:
    from bitcaster.models import Occurrence

    v1: Assignment = setup["assignments"][0]
    v2: Assignment = setup["assignments"][1]
    occurrence = setup["occurrence"]
    msg = setup["message"]

    addr = setup["address"]
    event = occurrence.event
    ch = setup["channel"]
    process_occurrence(occurrence.pk)
    assert sorted(ch.dispatcher._messages()) == sorted(
        [
            [addr.value, f"Message for {event.name} on channel {ch.name}", 0],
            [v2.address.value, f"Message for {event.name} on channel {ch.name}", 1],
        ]
    )
    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSED
    assert occurrence.data == {
        "delivered": [v1.id, v2.id],
        "recipients": [
            [v1.address.value, "test", v1.pk, ch.pk, setup["notification"].pk, msg.pk],
            [v2.address.value, "test", v2.pk, ch.pk, setup["notification"].pk, msg.pk],
        ],
        "errors": [],
        "channels": [ch.pk],
        "messages": [msg.pk],
        "notifications": [setup["notification"].pk],
    }


def test_process_incomplete_event(setup: "Context") -> None:
    from bitcaster.models import Occurrence

    ch = setup["channel"]
    occurrence = setup["occurrence"]
    v1, v2 = setup["assignments"]

    setup["occurrence"].data["delivered"] = [v1.id, v2.id]
    setup["occurrence"].data["recipients"] = []
    setup["occurrence"].save()

    process_occurrence(occurrence.pk)
    assert ch.dispatcher._messages() == []

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSED
    assert occurrence.data == {
        "delivered": [v1.id, v2.id],
        "recipients": [],
        "errors": [],
        "notifications": [setup["notification"].pk],
        "channels": [ch.pk],
        "messages": [],
    }


@pytest.mark.django_db(transaction=True)
def test_process_event_partially(setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.models import Occurrence

    v1: Assignment = setup["assignments"][0]

    msg: MessageTemplate = setup["message"]
    ch: Channel = setup["channel"]
    occurrence: Occurrence = setup["occurrence"]

    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel",
        mocked_notify := Mock(side_effect=[(None, msg.pk), Exception("This is raised after first call")]),
    )

    process_occurrence(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.NEW
    assert mocked_notify.call_count == 2
    assert occurrence.data == {
        "delivered": [setup["assignments"][0].id],
        "errors": ["Exception: This is raised after first call"],
        "recipients": [
            [v1.address.value, "test", v1.pk, ch.pk, setup["notification"].pk, msg.pk],
        ],
        "channels": [ch.pk],
        "messages": [msg.pk],
        "notifications": [setup["notification"].pk],
    }


def test_process_event_resume(setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.models import Occurrence

    ch: Channel = setup["channel"]
    n: Notification = setup["notification"]
    v1: Assignment = setup["assignments"][0]
    v2: Assignment = setup["assignments"][1]
    msg: MessageTemplate = setup["message"]
    occurrence = setup["occurrence"]
    # note: fake OccurrenceData. recipients does not contais a valid line
    occurrence.data = {"delivered": [v1.id], "recipients": [(v1.address.value, "test")]}
    occurrence.save()

    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel",
        mocked_notify := Mock(return_value=(None, msg.pk)),
    )

    process_occurrence(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSED
    assert mocked_notify.call_count == 1
    assert occurrence.data == {
        "delivered": [v1.id, v2.id],
        "recipients": [
            ["test1@example.com", "test"],
            ["test2@example.com", v2.channel.name, v2.pk, ch.pk, n.pk, msg.pk],
        ],
        "channels": [ch.pk],
        "notifications": [n.pk],
        "messages": [msg.pk],
        "errors": [],
    }


def test_silent_event(setup: "Context", monkeypatch: pytest.MonkeyPatch, system_objects: Any) -> None:
    from bitcaster.models import Occurrence

    cid = uuid.uuid4()
    e = setup["silent_event"]
    o = e.trigger(context={"key": "value"}, cid=cid)
    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", Mock())

    assert Occurrence.objects.system(correlation_id=cid).count() == 0
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.PROCESSED
    assert o.data == {
        "delivered": [],
        "recipients": [],
        "errors": [],
        "notifications": [],
        "channels": [],
        "messages": [],
    }
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value).count() == 1
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value, correlation_id=cid).count() == 1


def test_attempts(setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
    from testutils.factories import OccurrenceFactory

    from bitcaster.models import Occurrence

    o = OccurrenceFactory(attempts=0, status=Occurrence.Status.PROCESSED)
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.PROCESSED
    assert o.data == {}


def test_retry(setup: "Context", monkeypatch: pytest.MonkeyPatch, system_objects: Any) -> None:
    from bitcaster.models import Occurrence

    o = setup["occurrence"]
    v1 = setup["assignments"][0]
    ch = setup["channel"]
    n = setup["notification"]
    m = setup["message"]
    monkeypatch.setattr(
        "bitcaster.models.notification.Notification.notify_to_channel",
        mocked_notify := Mock(side_effect=[(None, 999), Exception("This is raised after first call")]),
    )
    for _a in range(10):
        process_occurrence(o.pk)
    o.refresh_from_db()
    assert o.attempts == 0
    assert o.status == Occurrence.Status.FAILED
    assert mocked_notify.call_count == 4
    assert o.data == {
        "delivered": [v1.id],
        "channels": [ch.pk],
        "messages": [m.pk],
        "notifications": [n.pk],
        "recipients": [[v1.address.value, "test", v1.pk, ch.pk, n.pk, m.pk]],
        "errors": [
            "Exception: This is raised after first call",
            "StopIteration: ",
            "StopIteration: ",
        ],
    }


def test_error(setup: "Context", system_objects: Any) -> None:
    from testutils.factories import OccurrenceFactory

    from bitcaster.models import Occurrence

    o = OccurrenceFactory(attempts=0, status=Occurrence.Status.NEW)
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.FAILED
    assert o.data == {}


def test_processed(setup: "Context", monkeypatch: pytest.MonkeyPatch, system_objects: Any) -> None:
    from testutils.factories import OccurrenceFactory

    from bitcaster.models import Occurrence

    monkeypatch.setattr("bitcaster.models.occurrence.Occurrence._process", mocked_notify := Mock())

    o = OccurrenceFactory(status=Occurrence.Status.PROCESSED)
    process_occurrence(o.pk)
    assert mocked_notify.call_count == 0


@pytest.fixture(autouse=True)
def run_tasks_sync(monkeypatch):
    import dramatiq
    from dramatiq.brokers.stub import StubBroker

    stub_broker = StubBroker()
    monkeypatch.setattr("bitcaster.runner.broker.broker", stub_broker)
    dramatiq.set_broker(stub_broker)


@pytest.mark.django_db(transaction=True)
def test_scan_occurrences(run_tasks_sync, setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.models import Occurrence

    monkeypatch.setattr("bitcaster.runner.tasks.process_occurrence.send", process_occurrence.fn)

    scan_occurrences()

    o: Occurrence = setup["occurrence"]
    o.refresh_from_db()
    assert o.recipients == 2
    assert o.status == Occurrence.Status.PROCESSED


@pytest.mark.django_db(transaction=True)
def test_process_silent(setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
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


@pytest.mark.django_db
def test_process_occurrence_return_value():
    from testutils.factories import OccurrenceFactory

    occ = OccurrenceFactory()
    with patch.object(Occurrence, "process", return_value=True):
        assert process_occurrence(occ.pk, return_value=True) is True


@pytest.mark.django_db
def test_process_occurrence_not_found():
    with pytest.raises(Occurrence.DoesNotExist):
        process_occurrence(-1)


@pytest.mark.django_db
def test_check_for_new_user_messages(monkeypatch):
    from testutils.factories import ChannelFactory, EventFactory, UserFactory

    user = UserFactory()
    monkeypatch.setattr("bitcaster.runner.tasks.get_users_to_notify", lambda: [user.pk])

    event = EventFactory()
    ChannelFactory(dispatcher=fqn(UserMessageDispatcher), config={"event": event.pk})

    with patch.object(Event, "trigger") as mock_trigger:
        with patch("bitcaster.runner.tasks.set_user_latest_notify_time") as mock_set_time:
            check_for_new_user_messages()
            mock_trigger.assert_called_once()
            mock_set_time.assert_called_once_with(user.pk)


@pytest.mark.django_db
def test_check_for_new_user_messages_no_channel(monkeypatch):
    from testutils.factories import UserFactory

    user = UserFactory()
    monkeypatch.setattr("bitcaster.runner.tasks.get_users_to_notify", lambda: [user.pk])
    # Ensure no UserMessageDispatcher channel exists
    Channel.objects.filter(dispatcher=fqn(UserMessageDispatcher)).delete()
    check_for_new_user_messages()


@pytest.mark.django_db
def test_check_for_new_user_messages_no_event(monkeypatch):
    from testutils.factories import ChannelFactory, UserFactory

    user = UserFactory()
    monkeypatch.setattr("bitcaster.runner.tasks.get_users_to_notify", lambda: [user.pk])
    # Channel exists but no event in config
    ChannelFactory(dispatcher=fqn(UserMessageDispatcher), config={})
    check_for_new_user_messages()


@pytest.mark.django_db
def test_check_for_new_user_messages_empty(monkeypatch):
    monkeypatch.setattr("bitcaster.runner.tasks.get_users_to_notify", list)
    check_for_new_user_messages()


@pytest.mark.django_db
def test_delete_expired_user_messages(system_user: "User") -> None:
    from datetime import timedelta

    from django.utils import timezone
    from testutils.factories import ChannelFactory, UserMessageFactory

    ChannelFactory(dispatcher=fqn(UserMessageDispatcher), config={"message_ttl": 7})

    m1 = UserMessageFactory()
    UserMessage.objects.filter(pk=m1.pk).update(created=timezone.now() - timedelta(days=10))

    m2 = UserMessageFactory()

    assert UserMessage.objects.count() == 2
    delete_expired_user_messages()
    assert UserMessage.objects.count() == 1
    assert UserMessage.objects.filter(pk=m2.pk).exists()


def test_monitor_run(system_user: "User", monitor) -> None:
    with patch("bitcaster.runner.tasks.monitor_check.send") as mock_send:
        monitor_run()
        assert mock_send.call_count == 1


def test_monitor_check(system_user: "User", monitor) -> None:
    assert monitor_check("-1") == "Monitor not found or deactivated"

    assert monitor_check(monitor.pk) == "done"

    with configure_model(monitor, active=False):
        assert monitor_check(monitor.pk) == "Monitor not found or deactivated"


@pytest.mark.django_db
def test_monitor_check_exception():
    from testutils.factories.monitor import MonitorFactory

    monitor = MonitorFactory(active=True)
    with patch.object(monitor.agent, "check", side_effect=Exception("Check failed")):
        with patch.object(Monitor.objects, "get", return_value=monitor):
            with pytest.raises(Exception, match="Check failed"):
                monitor_check(monitor.pk)
            monitor.refresh_from_db()
            assert monitor.active is False
            assert monitor.result == {"error": "Check failed"}


@pytest.mark.django_db
def test_purge_occurrences_exception():
    with patch.object(Occurrence.objects, "purgeable", side_effect=Exception("Database error")):
        result = purge_occurrences()
        assert isinstance(result, Exception)
        assert str(result) == "Database error"


@pytest.mark.django_db
def test_scan_occurrences_with_data():
    from testutils.factories import OccurrenceFactory

    occ = OccurrenceFactory(status=Occurrence.Status.NEW)
    with patch("bitcaster.runner.tasks.process_occurrence.send") as mock_send:
        result = scan_occurrences()
        assert occ.pk in result
        assert mock_send.call_count == 1


@pytest.mark.django_db
def test_scan_occurrences_empty():
    Occurrence.objects.filter(status=Occurrence.Status.NEW).delete()
    assert scan_occurrences() == []
