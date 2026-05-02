from unittest.mock import MagicMock, patch

import pytest
from strategy_field.utils import fqn
from testutils.agent import XAgent
from testutils.factories import ChannelFactory, EventFactory, MonitorFactory, OccurrenceFactory

from bitcaster.dispatchers import UserMessageDispatcher
from bitcaster.models import Event, Occurrence, UserMessage
from bitcaster.runner.tasks import (
    check_for_new_user_messages,
    delete_expired_user_messages,
    monitor_check,
    monitor_run,
    process_occurrence,
    purge_occurrences,
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
