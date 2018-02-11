# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from mercury_hangout import Hangout


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'sender': 'sender',
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': 'abc'},
                channel=channel)


def test_send(subscription):
    d = Hangout(channel)
    assert d.emit(subscription, 'subject', 'message') == 1


def test_connection(subscription1):
    d = Hangout(channel)
    assert d.test_connection()
