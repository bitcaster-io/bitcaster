from typing import TYPE_CHECKING, Any, TypedDict

import uuid

import freezegun
import pytest
from testutils.dispatcher import XDispatcher
from testutils.factories import ChannelFactory, MonitorFactory
from testutils.perms import configure_model
from unittest.mock import Mock, patch

from strategy_field.utils import fqn

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
            "event": Event,
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
    ev: Event = EventFactory.create(channels=[ch])
    v1: Assignment = AssignmentFactory.create(channel=ch, address__value="test1@example.com")
    v2: Assignment = AssignmentFactory.create(channel=ch, address__value="test2@example.com")
    no: Notification = NotificationFactory.create(event=ev, distribution__recipients=[v1, v2])
    msg = MessageTemplateFactory.create(
        channel=ch, event=no.event, content="Message for {{ event.name }} on channel {{channel.name}}"
    )

    bitcaster.initialize(admin_user)

    o = OccurrenceFactory.create(event=no.event, attempts=3, status=Occurrence.Status.NEW)
    return {
        "occurrence": o,
        "address": v1.address,
        "channel": ch,
        "event": ev,
        "message": msg,
        "assignments": [v1, v2],
        "notification": no,
        "silent_event": EventFactory.create(application__name="External"),
    }


@pytest.fixture
def monitor() -> "Monitor":
    return MonitorFactory.create()


@pytest.fixture
def user_messages(user: "User") -> "list[UserMessage]":
    """User messages fixture for filtering tests."""
    from testutils.factories import UserMessageFactory

    ChannelFactory.create(dispatcher=fqn(UserMessageDispatcher))
    m1 = UserMessageFactory.create(user=user, displayed=None, read=None)
    with freezegun.freeze_time("2000-01-01"):
        m2 = UserMessageFactory.create(user=user, displayed=True, read=None)
    return [m1, m2]


@pytest.mark.django_db(transaction=True)
def test_process_event_single(setup: "Context") -> None:
    from bitcaster.models import Occurrence

    v1: Assignment = setup["assignments"][0]
    v2: Assignment = setup["assignments"][1]
    occurrence = setup["occurrence"]
    msg = setup["message"]

    event = occurrence.event
    ch = setup["channel"]
    process_occurrence(occurrence.pk)
    assert ch.dispatcher._messages() == []
    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSING
    assert occurrence.recipients == 2
    assert occurrence.deliveries.count() == 2
    assert occurrence.data == {
        "delivered": [],
        "recipients": [
            [v1.address.value, "test", v1.pk, ch.pk, setup["notification"].pk, msg.pk],
            [v2.address.value, "test", v2.pk, ch.pk, setup["notification"].pk, msg.pk],
        ],
        "errors": [],
        "channels": [ch.pk],
        "messages": [msg.pk],
        "notifications": [setup["notification"].pk],
        "rendered": [
            {
                "assignment_pk": v1.pk,
                "notification_pk": setup["notification"].pk,
                "notification_name": setup["notification"].name,
                "channel_pk": ch.pk,
                "channel_name": ch.name,
                "address": v1.address.value,
                "subject": "",
                "message": f"Message for {event.name} on channel {ch.name}",
                "html_message": "",
            },
            {
                "assignment_pk": v2.pk,
                "notification_pk": setup["notification"].pk,
                "notification_name": setup["notification"].name,
                "channel_pk": ch.pk,
                "channel_name": ch.name,
                "address": v2.address.value,
                "subject": "",
                "message": f"Message for {event.name} on channel {ch.name}",
                "html_message": "",
            },
        ],
        "missing_template": [],
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
    assert occurrence.status == Occurrence.Status.PROCESSING
    assert occurrence.recipients == 2
    assert occurrence.deliveries.count() == 2
    assert occurrence.data["delivered"] == []
    assert occurrence.data["recipients"] != []


@pytest.mark.django_db(transaction=True)
def test_process_event_partially(setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.models import Delivery, Occurrence

    v1: Assignment = setup["assignments"][0]
    v2: Assignment = setup["assignments"][1]

    occurrence: Occurrence = setup["occurrence"]

    monkeypatch.setattr(
        "bitcaster.models.messagetemplate.MessageTemplate.render",
        mocked_render := Mock(side_effect=[("s", "m", "h"), Exception("This is raised after first call")]),
    )

    process_occurrence(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSING
    assert mocked_render.call_count == 2
    assert occurrence.data["errors"] == ["Exception: This is raised after first call"]
    assert occurrence.data["delivered"] == []
    assert occurrence.deliveries.count() == 2
    (ok_delivery,) = occurrence.deliveries.filter(assignment=v1)
    assert ok_delivery.status == Delivery.Status.PENDING
    assert ok_delivery.rendered == {"subject": "s", "message": "m", "html_message": "h"}
    (failed_delivery,) = occurrence.deliveries.filter(assignment=v2)
    assert failed_delivery.status == Delivery.Status.FAILURE
    assert failed_delivery.data["render_error"] is True


def test_process_event_resume(setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.models import Delivery, Occurrence

    n: Notification = setup["notification"]
    v1: Assignment = setup["assignments"][0]
    v2: Assignment = setup["assignments"][1]
    msg: MessageTemplate = setup["message"]
    occurrence = setup["occurrence"]
    ch = setup["channel"]

    Delivery.objects.create(
        occurrence=occurrence,
        assignment=v1,
        notification=n,
        channel=ch,
        message_template=msg,
        status=Delivery.Status.DELIVERED,
    )
    occurrence.status = Occurrence.Status.NEW
    occurrence.save()

    process_occurrence(occurrence.pk)

    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSING
    assert occurrence.recipients == 2
    assert occurrence.deliveries.count() == 2
    assert occurrence.deliveries.filter(assignment=v1, status=Delivery.Status.DELIVERED).exists()
    (v2_delivery,) = occurrence.deliveries.filter(assignment=v2)
    assert v2_delivery.status == Delivery.Status.PENDING
    assert occurrence.data["delivered"] == []


def test_silent_event(setup: "Context", monkeypatch: pytest.MonkeyPatch, system_objects: Any) -> None:
    from bitcaster.models import Occurrence

    cid = uuid.uuid4()
    e = setup["silent_event"]
    o = e.trigger(context={"key": "value"}, cid=cid)
    monkeypatch.setattr("bitcaster.models.notification.Notification.notify_to_channel", Mock())

    assert Occurrence.objects.system(correlation_id=cid).count() == 0
    process_occurrence(o.pk)

    o.refresh_from_db()
    assert o.status == Occurrence.Status.PROCESSING
    assert o.data == {
        "delivered": [],
        "recipients": [],
        "errors": [],
        "notifications": [],
        "channels": [],
        "messages": [],
        "rendered": [],
        "missing_template": [],
    }
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value).count() == 1
    assert Occurrence.objects.system(event__name=SystemEvent.OCCURRENCE_SILENCE.value, correlation_id=cid).count() == 1


def test_attempts(setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.models import Occurrence

    o: Occurrence = setup["occurrence"]
    with configure_model(o, attempts=0, status=Occurrence.Status.PROCESSING):
        assert o.status == Occurrence.Status.PROCESSING
        process_occurrence(o.pk)

        o.refresh_from_db()
        assert o.status == Occurrence.Status.PROCESSING
        assert o.data == {}


def test_retry(setup: "Context", monkeypatch: pytest.MonkeyPatch, system_objects: Any) -> None:
    from bitcaster.models import Occurrence

    o = setup["occurrence"]
    monkeypatch.setattr(
        "bitcaster.models.occurrence.Occurrence._process",
        mocked_process := Mock(side_effect=Exception("This is raised after first call")),
    )
    for _a in range(10):
        process_occurrence(o.pk)
    o.refresh_from_db()
    assert o.status == Occurrence.Status.NEW  # failure rolls back the attempt decrement
    assert mocked_process.call_count == 10
    assert o.data == {}


def test_error(setup: "Context", system_objects: Any) -> None:
    from bitcaster.models import Occurrence

    o: Occurrence = setup["occurrence"]
    with configure_model(o, attempts=0, status=Occurrence.Status.NEW):
        process_occurrence(o.pk)

        o.refresh_from_db()
        assert o.status == Occurrence.Status.FAILED
        assert o.data == {}


def test_processed(setup: "Context", monkeypatch: pytest.MonkeyPatch, system_objects: Any) -> None:
    from bitcaster.models import Occurrence

    monkeypatch.setattr("bitcaster.models.occurrence.Occurrence._process", mocked_notify := Mock())

    o: Occurrence = setup["occurrence"]
    with configure_model(o, attempts=0, status=Occurrence.Status.PROCESSING):
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
    assert o.status == Occurrence.Status.PROCESSING


@pytest.mark.django_db(transaction=True)
def test_process_silent(setup: "Context", monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.models import Event, Occurrence

    monkeypatch.setattr("bitcaster.models.occurrence.Occurrence.process", mocked_notify := Mock())

    silent_event = Event.objects.get(name=SystemEvent.OCCURRENCE_SILENCE.value)
    o: Occurrence = setup["occurrence"]
    with configure_model(o, status=Occurrence.Status.NEW, event=silent_event):
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
def test_process_occurrence_return_value(setup):
    o: Occurrence = setup["occurrence"]
    with configure_model(o, status=Occurrence.Status.NEW):
        with patch.object(Occurrence, "process", return_value=True):
            assert process_occurrence(o.pk, return_value=True) is True


@pytest.mark.django_db
def test_process_occurrence_not_found():
    with pytest.raises(Occurrence.DoesNotExist):
        process_occurrence(-1)


@pytest.mark.django_db
def test_check_for_new_user_messages(setup, monkeypatch):
    user = setup["address"].user
    event = setup["event"]
    channel = setup["channel"]

    monkeypatch.setattr("bitcaster.runner.tasks.get_users_to_notify", lambda: [user.pk])
    with configure_model(channel, dispatcher=fqn(UserMessageDispatcher), config={"event": event.pk}):
        with patch.object(Event, "trigger") as mock_trigger:
            with patch("bitcaster.runner.tasks.set_user_latest_notify_time") as mock_set_time:
                check_for_new_user_messages()
                mock_trigger.assert_called_once()
                mock_set_time.assert_called_once_with(user.pk)


@pytest.mark.django_db
def test_check_for_new_user_messages_no_channel(user, monkeypatch):
    monkeypatch.setattr("bitcaster.runner.tasks.get_users_to_notify", lambda: [user.pk])
    # Ensure no UserMessageDispatcher channel exists
    Channel.objects.filter(dispatcher=fqn(UserMessageDispatcher)).delete()
    check_for_new_user_messages()


@pytest.mark.django_db
def test_check_for_new_user_messages_no_event(user, monkeypatch, channel):
    monkeypatch.setattr("bitcaster.runner.tasks.get_users_to_notify", lambda: [user.pk])
    # Channel exists but no event in config
    with configure_model(channel, dispatcher=fqn(UserMessageDispatcher), config={}):
        check_for_new_user_messages()


@pytest.mark.django_db
def test_check_for_new_user_messages_empty(monkeypatch):
    monkeypatch.setattr("bitcaster.runner.tasks.get_users_to_notify", list)
    check_for_new_user_messages()


@pytest.mark.django_db
def test_delete_expired_user_messages(user_messages, system_user: "User") -> None:
    m1, m2 = user_messages
    assert UserMessage.objects.count() == 2
    assert UserMessage.objects.expired().count() == 1
    delete_expired_user_messages()
    assert UserMessage.objects.count() == 1
    assert UserMessage.objects.filter(pk=m1.pk).exists()
    assert not UserMessage.objects.filter(pk=m2.pk).exists()


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
def test_monitor_check_exception(monitor):
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
def test_scan_occurrences_with_data(occurrence):
    with patch("bitcaster.runner.tasks.process_occurrence.send") as mock_send:
        result = scan_occurrences()
        assert occurrence.pk in result
        assert mock_send.call_count == 1


@pytest.mark.django_db
def test_scan_occurrences_empty():
    Occurrence.objects.filter(status=Occurrence.Status.NEW).delete()
    assert scan_occurrences() == []
