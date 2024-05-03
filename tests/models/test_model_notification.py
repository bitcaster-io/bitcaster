from typing import TYPE_CHECKING
from unittest.mock import Mock

from testutils.factories import NotificationFactory
from testutils.factories.channel import ChannelFactory
from testutils.factories.message import MessageFactory

if TYPE_CHECKING:
    from bitcaster.models import Event, Notification


def test_get_message_cache(notification: "Notification", django_assert_num_queries):
    ch1 = ChannelFactory()
    m1 = MessageFactory(channel=ch1, notification=notification, event=notification.event)

    with django_assert_num_queries(1):
        assert notification.get_message(ch1) == m1
        assert notification.get_message(ch1) == m1
        assert notification.get_message(ch1) == m1


def test_get_message_precedence(event: "Event", django_assert_num_queries):
    ch1 = ChannelFactory()
    n1: "Notification" = NotificationFactory(event=event)
    n2: "Notification" = NotificationFactory(event=event)

    m1: "Notification" = MessageFactory(name="m1", channel=ch1, event=n1.event, notification=None)
    m2: "Notification" = MessageFactory(name="m2", channel=ch1, event=n1.event, notification=n2)

    assert list(n1.get_messages(ch1)) == [m1]
    assert list(n2.get_messages(ch1)) == [m2, m1]

    with django_assert_num_queries(2):
        assert n1.get_message(ch1) == m1
        assert n1.get_message(ch1) == m1

        assert n2.get_message(ch1) == m2
        assert n2.get_message(ch1) == m2


def test_missing_message(event, monkeypatch):
    ch1 = ChannelFactory()
    n1: "Notification" = NotificationFactory(event=event)
    monkeypatch.setattr(ch1.dispatcher, "send", mocked_notify := Mock())

    ret = n1.notify_to_channel(ch1, Mock(), {})
    assert ret is None
    assert mocked_notify.call_count == 0
