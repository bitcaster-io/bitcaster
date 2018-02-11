# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest

from mercury_twilio import Twilio


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'sid': 'aaa',
                           'sender': 'sender',
                           'token': 'bbb'})
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': 'abc'},
                channel=channel)


def test_gmail(subscription):
    d = Twilio(subscription.channel)
    assert d.emit(subscription, 'subject', 'message') == 1


def test_gmail_test_connection(subscription):
    d = Twilio(subscription.channel)
    assert d.test_connection()
