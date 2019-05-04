from unittest import mock
from unittest.mock import Mock

import pytest
from django.core.exceptions import ObjectDoesNotExist

from bitcaster.exceptions import MaxChannelError
from bitcaster.models import Channel
from bitcaster.tasks import emit_event, process_event


@pytest.mark.django_db
def test_process_event(subscription1):
    channel = subscription1.channel
    event = subscription1.event
    assert process_event(channel, event, {})


@pytest.mark.django_db
def test_process_event_errors_threshold(subscription1):
    channel = subscription1.channel
    channel.errors_threshold = 0
    event = subscription1.event
    with pytest.raises(MaxChannelError):
        with mock.patch('bitcaster.models.Notification.log'):
            with mock.patch('bitcaster.models.Channel.handler',
                            Mock(side_effect=Mock(side_effect=Exception))):
                assert process_event(channel, event, {})
    assert not channel.enabled


@pytest.mark.django_db
def test_process_event_no_messages(subscription1):
    channel = subscription1.channel
    channel.messages.all().delete()
    event = subscription1.event
    with pytest.raises(ObjectDoesNotExist):
        assert process_event(channel, event, {})


@pytest.mark.django_db
def test_process_disabled_event(subscription1):
    channel = Channel(enabled=False)
    assert process_event(channel, Mock(), {}) == (0, 0)


@pytest.mark.django_db
def test_emit_event(event1):
    assert emit_event(event1, {})
