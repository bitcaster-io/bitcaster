import contextlib
import logging
from typing import TYPE_CHECKING

import pytest
from dramatiq import Worker
from strategy_field.utils import fqn

from bitcaster.console.utils import get_user_latest_notify_time
from bitcaster.dispatchers import UserMessageDispatcher
from bitcaster.runner.tasks import check_for_new_user_messages, scan_occurrences

if TYPE_CHECKING:
    from bitcaster.models import Channel, Event, User, UserMessage


@contextlib.contextmanager
def stub_worker():
    from bitcaster.runner.broker import broker

    worker = Worker(broker, worker_timeout=100)
    worker.start()
    yield worker
    worker.stop()


@pytest.fixture
def data(db) -> "tuple[Channel, Event, UserMessage]":
    from testutils.factories import (
        AssignmentFactory,
        ChannelFactory,
        EventFactory,
        MessageTemplateFactory,
        NotificationFactory,
        UserMessageFactory,
    )

    ch1 = ChannelFactory.create(name="XDispatcher")

    event: "Event" = EventFactory.create(channels=[ch1])
    MessageTemplateFactory(channel=ch1, event=event)
    NotificationFactory.create(event=event, external_filtering=True, dynamic=False, distribution=None)
    ch2 = ChannelFactory.create(
        name="UserMessageDispatcher", dispatcher=fqn(UserMessageDispatcher), config={"event": event.pk, "active": True}
    )
    user_message: UserMessage = UserMessageFactory.create(event=event)
    AssignmentFactory.create(
        channel=ch2,
        address__value=user_message.user.email,
        address__user=user_message.user,
        active=True,
        validated=True,
    )
    AssignmentFactory.create(
        channel=ch1,
        address__value=user_message.user.email,
        address__user=user_message.user,
        active=True,
        validated=True,
    )
    return ch1, event, user_message


@pytest.mark.django_db(transaction=True)
def test_console_check_for_new_user_messages(data: "tuple[Channel, Event, UserMessage]"):
    from testutils.factories import UserMessageFactory

    from bitcaster.models import Occurrence

    channel, event, message = data
    check_for_new_user_messages()
    assert Occurrence.objects.filter(event=event, status=Occurrence.Status.NEW).count() == 1

    check_for_new_user_messages()  # no new data, no page visited: not new occurrence
    assert Occurrence.objects.filter(event=event, status=Occurrence.Status.NEW).count() == 1

    o = Occurrence.objects.get(event=event, status=Occurrence.Status.NEW)
    assert o.options == {"filters": {"exclude": [], "include": [{"pk__in": [message.user.pk]}]}}

    UserMessageFactory.create()
    check_for_new_user_messages()  # new message new occurrence created
    assert Occurrence.objects.filter(event=event, status=Occurrence.Status.NEW).count() == 2


@pytest.mark.django_db(transaction=True)
def test_console_notify_new_messages(django_app, broker, data: "tuple[Channel, Event, UserMessage]", caplog):
    from testutils.factories import UserMessageFactory

    caplog.set_level(logging.ERROR)
    channel, event, message = data
    user: "User" = message.user

    check_for_new_user_messages()
    with stub_worker():
        scan_occurrences()
    messages = channel.dispatcher._messages()
    assert len(messages) == 1
    assert messages[0][0] == user.email

    # create_new_message
    UserMessageFactory.create(user=user, event=event, message="abc")
    with stub_worker():
        scan_occurrences()

    messages = channel.dispatcher._messages()
    assert len(messages) == 1
    assert messages[0][0] == user.email
    latest_notify_time = get_user_latest_notify_time(user.pk)

    msg = UserMessageFactory.create(user=user, event=event)
    assert msg.created > latest_notify_time
    check_for_new_user_messages()
    with stub_worker():
        scan_occurrences()

    messages = channel.dispatcher._messages()
    assert len(messages) == 2
