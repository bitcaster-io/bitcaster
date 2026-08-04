import pytest
from testutils.agent import XAgent
from testutils.factories import (
    ChannelFactory,
    DeliveryFactory,
    EventFactory,
    EventSimulationFactory,
    MonitorFactory,
    OccurrenceFactory,
)
from unittest.mock import MagicMock, Mock, patch

from strategy_field.utils import fqn

from bitcaster.dispatchers import UserMessageDispatcher
from bitcaster.models import Delivery, Event, EventSimulation, Occurrence, UserMessage
from bitcaster.runner.tasks import (
    check_for_new_user_messages,
    delete_expired_user_messages,
    monitor_check,
    monitor_run,
    process_deliveries_page,
    process_occurrence,
    purge_event_simulations,
    purge_occurrences,
    run_event_simulation,
    scan_occurrences,
)

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def monitor():
    return MonitorFactory(active=True)


def test_process_occurrence_success():
    occ = OccurrenceFactory()
    with patch.object(Occurrence, "process", return_value=5) as mock_process:
        result = process_occurrence(occ.pk, return_value=True)
        assert result == 5
        mock_process.assert_called_once()


def test_process_occurrence_no_return_value():
    occ = OccurrenceFactory()
    with patch.object(Occurrence, "process", return_value=5):
        result = process_occurrence(occ.pk, return_value=False)
        assert result is None


def test_process_occurrence_not_found():
    with pytest.raises(Occurrence.DoesNotExist):
        process_occurrence(9999)


def test_scan_occurrences():
    occ = OccurrenceFactory(status=Occurrence.Status.NEW)
    # Occorrenza in pausa non dovrebbe essere processata
    paused_event = EventFactory(paused=True)
    OccurrenceFactory(status=Occurrence.Status.NEW, event=paused_event)

    with patch("bitcaster.runner.tasks.process_occurrence.send") as mock_send:
        result = scan_occurrences()
        assert occ.pk in result
        assert len(result) == 1
        mock_send.assert_called_once_with(occ.pk)


def test_delete_expired_user_messages():
    with patch.object(UserMessage.objects, "expired") as mock_expired:
        mock_query = MagicMock()
        mock_expired.return_value = mock_query
        delete_expired_user_messages()
        mock_query.delete.assert_called_once()


def test_purge_occurrences():
    occ = OccurrenceFactory()
    # Mocking the purgeable manager method or the queryset
    with patch.object(Occurrence.objects, "purgeable") as mock_purgeable:
        mock_query = MagicMock()
        mock_purgeable.return_value = mock_query
        mock_query.order_by.return_value.values_list.return_value.__getitem__.return_value = [occ.pk]

        # Simula un ciclo e poi esce
        mock_query.order_by.return_value.values_list.return_value.__getitem__.side_effect = [[occ.pk], []]

        purge_occurrences(max_batches=1)
        # Verifica che delete sia stato chiamato (tramite il filtro degli ID)
        assert Occurrence.objects.filter(pk=occ.pk).count() == 0


def test_purge_occurrences_empty():
    with patch.object(Occurrence.objects, "purgeable") as mock_purgeable:
        mock_query = MagicMock()
        mock_purgeable.return_value = mock_query
        mock_query.order_by.return_value.values_list.return_value.__getitem__.return_value = []
        purge_occurrences(max_batches=1)


def test_purge_occurrences_exception():
    with patch.object(Occurrence.objects, "purgeable", side_effect=Exception("Purge error")):
        res = purge_occurrences()
        assert isinstance(res, Exception)
        assert str(res) == "Purge error"


def test_run_event_simulation_success():
    from constance.test.pytest import override_config

    sim = EventSimulationFactory(mode="full")
    with override_config(DEBUG_PREVIEW_RENDER_LIMIT=2):
        with patch(
            "bitcaster.models.occurrence.Occurrence.preview", return_value=(True, {"delivered": []})
        ) as mock_preview:
            run_event_simulation(sim.pk)
    sim.refresh_from_db()
    assert sim.status == Occurrence.Status.PROCESSING.value
    assert sim.data["recipients_count"] == 0
    assert sim.data["delivered"] == []
    mock_preview.assert_called_once()


def test_run_event_simulation_partial_uses_limit():
    from constance.test.pytest import override_config

    sim = EventSimulationFactory(mode="partial")
    with override_config(DEBUG_PREVIEW_RENDER_LIMIT=7):
        with patch("bitcaster.models.occurrence.Occurrence.preview", return_value=(True, {})) as mock_preview:
            run_event_simulation(sim.pk)
    mock_preview.assert_called_once()
    assert mock_preview.call_args.args == ("partial", 7)


def test_run_event_simulation_failed():
    sim = EventSimulationFactory(mode="full")
    with patch("bitcaster.models.occurrence.Occurrence.preview", side_effect=Exception("Boom")):
        run_event_simulation(sim.pk)
    sim.refresh_from_db()
    assert sim.status == Occurrence.Status.FAILED.value
    assert sim.data["errors"] == ["Exception: Boom"]


def test_run_event_simulation_not_found():
    run_event_simulation(9999)  # should not raise


def test_run_event_simulation_does_not_overwrite_processed():
    """Atomic status guard: a concurrent completion is not overwritten by the task."""

    sim = EventSimulationFactory(mode="full", status=Occurrence.Status.PROCESSING.value, data={"errors": []})
    with patch("bitcaster.models.occurrence.Occurrence.preview", return_value=(True, {"delivered": [1]})):
        run_event_simulation(sim.pk)
    sim.refresh_from_db()
    assert sim.status == Occurrence.Status.PROCESSING.value
    assert sim.data == {"errors": []}


def test_purge_event_simulations():
    from freezegun import freeze_time

    from django.utils import timezone

    with freeze_time(timezone.now()):
        sim = EventSimulationFactory()
    with freeze_time(timezone.now().replace(year=2000)):
        old_sim = EventSimulationFactory()

    purge_event_simulations()
    assert not EventSimulation.objects.filter(pk=old_sim.pk).exists()
    assert EventSimulation.objects.filter(pk=sim.pk).exists()


def test_purge_event_simulations_empty():
    with patch.object(EventSimulation.objects, "purgeable") as mock_purgeable:
        mock_query = MagicMock()
        mock_purgeable.return_value = mock_query
        mock_query.order_by.return_value.values_list.return_value.__getitem__.return_value = []
        purge_event_simulations(max_batches=1)


def test_purge_event_simulations_stops_at_max_batches():
    with patch.object(EventSimulation.objects, "purgeable") as mock_purgeable:
        mock_query = MagicMock()
        mock_purgeable.return_value = mock_query
        mock_query.order_by.return_value.values_list.return_value.__getitem__.return_value = [1]
        purge_event_simulations(max_batches=1)


def test_purge_event_simulations_exception():
    with patch.object(EventSimulation.objects, "purgeable", side_effect=Exception("Purge error")):
        res = purge_event_simulations()
        assert isinstance(res, Exception)
        assert str(res) == "Purge error"


def test_monitor_run():
    m1 = MonitorFactory(active=True)
    MonitorFactory(active=False)
    with patch("bitcaster.runner.tasks.monitor_check.send") as mock_send:
        monitor_run()
        mock_send.assert_called_once_with(m1.pk)


def test_monitor_check_success(monitor):
    from django.contrib.admin.models import LogEntry
    from django.contrib.contenttypes.models import ContentType

    with patch.object(XAgent, "check"):
        with patch.object(XAgent, "changes_detected", return_value=True):
            res = monitor_check(monitor.pk)
            assert res == "done"
            monitor.refresh_from_db()
            assert monitor.result["changes"] is True
            assert LogEntry.objects.filter(
                content_type=ContentType.objects.get_for_model(monitor), object_id=monitor.pk, action_flag=100
            ).exists()


def test_monitor_check_error():
    m = MonitorFactory(active=True)
    with patch.object(XAgent, "check", side_effect=Exception("Agent error")):
        with pytest.raises(Exception, match="Agent error"):
            monitor_check(m.pk)
        m.refresh_from_db()
        assert m.active is False
        assert "Agent error" in m.result["error"]


def test_monitor_check_monitor_not_found():
    result = monitor_check(99999)
    assert result == "Monitor not found or deactivated"


def test_check_for_new_user_messages_no_users():
    with patch("bitcaster.runner.tasks.get_users_to_notify", return_value=[]):
        check_for_new_user_messages()
        # Non dovrebbe fare nulla


def test_check_for_new_user_messages_no_channel(user):
    from bitcaster.models import Channel

    Channel.objects.filter(dispatcher=fqn(UserMessageDispatcher)).delete()
    with patch("bitcaster.runner.tasks.get_users_to_notify", return_value=[user.pk]):
        check_for_new_user_messages()


def test_check_for_new_user_messages_no_event(user):
    # Channel without event in config
    ChannelFactory(dispatcher=fqn(UserMessageDispatcher), config={})
    with patch("bitcaster.runner.tasks.get_users_to_notify", return_value=[user.pk]):
        check_for_new_user_messages()


def test_check_for_new_user_messages_with_users(user):
    event = EventFactory()
    ChannelFactory(dispatcher=fqn(UserMessageDispatcher), config={"event": event.pk})

    with patch("bitcaster.runner.tasks.get_users_to_notify", return_value=[user.pk]):
        with patch.object(Event, "trigger") as mock_trigger:
            with patch("bitcaster.runner.tasks.set_user_latest_notify_time") as mock_set_time:
                check_for_new_user_messages()
                mock_trigger.assert_called_once()
                mock_set_time.assert_called_once_with(user.pk)


@pytest.fixture
def delivery_setup():
    from testutils.factories import AssignmentFactory, ChannelFactory, MessageTemplateFactory, NotificationFactory

    notification = NotificationFactory.create(event__channels=[ChannelFactory()])
    channel = notification.event.channels.first()
    asm = AssignmentFactory(channel=channel)
    MessageTemplateFactory(channel=channel, event=notification.event, content="Hello {{ foo }}")
    notification.distribution.recipients.add(asm)
    occurrence = notification.event.trigger(context={"foo": "bar"})
    occurrence.process()
    return occurrence, asm, notification, channel


def _add_delivery(occurrence, notification, channel, status, next_attempt_at=None):
    from testutils.factories import AddressFactory, AssignmentFactory

    assignment = AssignmentFactory(address=AddressFactory(), channel=channel)
    return DeliveryFactory.create(
        occurrence=occurrence,
        assignment=assignment,
        notification=notification,
        channel=channel,
        status=status,
        next_attempt_at=next_attempt_at,
    )


def test_process_deliveries_page_sends_only_due(delivery_setup):
    from django.utils import timezone

    occurrence, _asm, notification, channel = delivery_setup
    (due_pending,) = occurrence.deliveries.all()

    due_error = _add_delivery(
        occurrence, notification, channel, Delivery.Status.ERROR, timezone.now() - timezone.timedelta(hours=1)
    )
    _add_delivery(
        occurrence, notification, channel, Delivery.Status.ERROR, timezone.now() + timezone.timedelta(hours=1)
    )
    _add_delivery(occurrence, notification, channel, Delivery.Status.FAILURE)

    with patch.object(Delivery, "send", autospec=True) as mock_send:
        result = process_deliveries_page()
    assert result == 2
    sent = {call.args[0].pk for call in mock_send.call_args_list}
    assert sent == {due_pending.pk, due_error.pk}


def test_process_deliveries_page_delivered_on_success(delivery_setup):
    from testutils.dispatcher import XDispatcher

    occurrence, *_ = delivery_setup
    (delivery,) = occurrence.deliveries.all()
    with patch.object(XDispatcher, "_send", Mock(return_value=True)):
        process_deliveries_page()
    delivery.refresh_from_db()
    assert delivery.status == Delivery.Status.DELIVERED


def test_process_deliveries_page_error_schedules_retry(delivery_setup):
    from testutils.dispatcher import XDispatcher

    from bitcaster.exceptions import DispatcherError

    occurrence, *_ = delivery_setup
    (delivery,) = occurrence.deliveries.all()
    with patch.object(XDispatcher, "_send", Mock(side_effect=DispatcherError("boom"))):
        process_deliveries_page()
    delivery.refresh_from_db()
    assert delivery.status == Delivery.Status.ERROR
    assert delivery.errors == 1
    assert delivery.next_attempt_at is not None


def test_process_deliveries_page_max_retries_sets_failure(delivery_setup):
    from constance.test.pytest import override_config

    from testutils.dispatcher import XDispatcher

    from bitcaster.exceptions import DispatcherError

    occurrence, *_ = delivery_setup
    (delivery,) = occurrence.deliveries.all()
    with patch.object(XDispatcher, "_send", Mock(side_effect=DispatcherError("boom"))):
        with override_config(MAX_DELIVERY_RETRIES=1):
            process_deliveries_page()
    delivery.refresh_from_db()
    assert delivery.status == Delivery.Status.FAILURE
    assert delivery.next_attempt_at is None


def test_process_deliveries_page_uses_page_size(delivery_setup):
    from constance.test.pytest import override_config

    occurrence, _asm, notification, channel = delivery_setup
    _add_delivery(occurrence, notification, channel, Delivery.Status.PENDING)
    with override_config(DELIVERY_PAGE_SIZE=1):
        with patch.object(Delivery, "send") as mock_send:
            process_deliveries_page()
    assert mock_send.call_count == 1


def test_process_records_phase1_timestamp(delivery_setup):
    occurrence, *_ = delivery_setup
    occurrence.refresh_from_db()
    assert occurrence.data["processing"]["phase1_at"]
    assert occurrence.data["processing"]["phase2_attempts"] == []


def test_process_deliveries_page_records_phase2_attempts(delivery_setup):
    from testutils.dispatcher import XDispatcher

    occurrence, *_ = delivery_setup
    (delivery,) = occurrence.deliveries.all()
    with patch.object(XDispatcher, "_send", Mock(side_effect=Exception("boom"))):
        process_deliveries_page()
    occurrence.refresh_from_db()
    attempts = occurrence.data["processing"]["phase2_attempts"]
    assert len(attempts) == 1
    assert attempts[0]["processed"] == 1
    assert attempts[0]["at"]


def test_scan_occurrences_marks_completed_when_no_pending_deliveries():
    """Lines 132-136,138: PROCESSING occurrences with no pending deliveries marked COMPLETED."""

    occurrence = OccurrenceFactory(
        status=Occurrence.Status.PROCESSING,
        data={"processing": {"phase2_attempts": []}},
    )
    with patch("bitcaster.runner.tasks.logger") as mock_logger:
        scan_occurrences()
        occurrence.refresh_from_db()
        assert occurrence.status == Occurrence.Status.COMPLETED
        assert occurrence.data["processing"]["finished_at"]
        mock_logger.info.assert_called_once()


def test_scan_occurrences_skips_processing_with_pending_deliveries():
    """Lines 132: occurrences with pending deliveries stay PROCESSING."""
    from bitcaster.models import Delivery

    occurrence = OccurrenceFactory(
        status=Occurrence.Status.PROCESSING,
        data={"processing": {"phase2_attempts": []}},
    )
    DeliveryFactory(occurrence=occurrence, status=Delivery.Status.PENDING)
    scan_occurrences()
    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.PROCESSING


def test_scan_occurrences_skips_non_processing():
    """Lines 131: only PROCESSING occurrences are checked."""
    occurrence = OccurrenceFactory(status=Occurrence.Status.COMPLETED)
    scan_occurrences()
    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.COMPLETED


def test_process_deliveries_page_records_finished_at(delivery_setup):
    from testutils.dispatcher import XDispatcher

    occurrence, *_ = delivery_setup
    (delivery,) = occurrence.deliveries.all()
    with patch.object(XDispatcher, "_send", Mock(return_value=True)):
        process_deliveries_page()
    occurrence.refresh_from_db()
    assert occurrence.status == Occurrence.Status.COMPLETED
    assert occurrence.data["processing"]["finished_at"]
    assert len(occurrence.data["processing"]["phase2_attempts"]) == 1
