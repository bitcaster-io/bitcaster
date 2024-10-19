from typing import TYPE_CHECKING, Any
from unittest.mock import Mock

import pytest
from pytest_django import DjangoAssertNumQueries
from testutils.factories import NotificationFactory
from testutils.factories.channel import ChannelFactory
from testutils.factories.message import MessageFactory

if TYPE_CHECKING:
    from pytest import MonkeyPatch

    from bitcaster.models import Event, Message, Notification


def test_get_message_cache(notification: "Notification", django_assert_num_queries: DjangoAssertNumQueries) -> None:
    ch1 = ChannelFactory()
    m1 = MessageFactory(channel=ch1, notification=notification, event=notification.event)

    with django_assert_num_queries(1):
        assert notification.get_message(ch1) == m1
        assert notification.get_message(ch1) == m1
        assert notification.get_message(ch1) == m1


def test_get_message_precedence(event: "Event", django_assert_num_queries: DjangoAssertNumQueries) -> None:
    ch1 = ChannelFactory()
    n1: "Notification" = NotificationFactory(event=event)
    n2: "Notification" = NotificationFactory(event=event)

    m1: "Message" = MessageFactory(name="m1", channel=ch1, event=n1.event, notification=None)
    m2: "Message" = MessageFactory(name="m2", channel=ch1, event=n1.event, notification=n2)

    assert list(n1.get_messages(ch1)) == [m1]
    assert list(n2.get_messages(ch1)) == [m2, m1]

    with django_assert_num_queries(2):
        assert n1.get_message(ch1) == m1
        assert n1.get_message(ch1) == m1

        assert n2.get_message(ch1) == m2
        assert n2.get_message(ch1) == m2


def test_missing_message(event: "Event", monkeypatch: "MonkeyPatch") -> None:
    ch1 = ChannelFactory()
    n1: "Notification" = NotificationFactory(event=event)
    monkeypatch.setattr(ch1.dispatcher, "send", mocked_notify := Mock())

    ret = n1.notify_to_channel(ch1, Mock(), {})
    assert ret is None
    assert mocked_notify.call_count == 0


@pytest.mark.parametrize(
    "ctx, extra, expected",
    [
        pytest.param({}, {}, {}, id="all-empty"),
        pytest.param({}, {"new": 123}, {"new": 123}, id="contribute"),
        pytest.param({"a": 1, "b": 2, "c": 3}, {"b": 99}, {"a": 1, "b": 99, "c": 3}, id="override-b"),
        pytest.param({"a": 1, "b": 2}, {}, {"a": 1, "b": 2}, id="no-override"),
        pytest.param({"notification": 1, "b": 2}, {}, {"b": 2}, id="override-element"),
    ],
)
def test_extra_context_override(ctx: dict[str, str], extra: dict[str, Any], expected: dict[str, Any]) -> None:
    notification = NotificationFactory(extra_context=extra)
    expected |= {"notification": notification.name}
    assert notification.get_context(ctx) == expected
