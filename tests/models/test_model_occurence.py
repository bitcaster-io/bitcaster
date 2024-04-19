from typing import TYPE_CHECKING

from testutils.factories.channel import ChannelFactory
from testutils.factories.message import MessageFactory

if TYPE_CHECKING:
    from bitcaster.models import Event


def test_get_message(event: "Event", django_assert_num_queries):
    ch1 = ChannelFactory()
    ch2 = ChannelFactory()
    m0 = MessageFactory(channel=None, event=event)
    m1 = MessageFactory(channel=ch1, event=event)

    with django_assert_num_queries(1):
        assert event.get_message(ch1) == m1
        assert event.get_message(ch1) == m1
        assert event.get_message(ch1) == m1

    with django_assert_num_queries(1):
        assert event.get_message(ch2) == m0
        assert event.get_message(ch2) == m0

    with django_assert_num_queries(0):
        assert event.get_message(ch1) == m1
        assert event.get_message(ch2) == m0
