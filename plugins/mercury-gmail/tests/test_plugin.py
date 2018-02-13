# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from environ import Env
from pathlib import Path

from mercury.exceptions import PluginValidationError

from mercury_gmail import Gmail


env = Env(MERCURY_GMAIL_USERNAME='',
          MERCURY_GMAIL_PASSWORD='',
          MERCURY_GMAIL_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'username': env('MERCURY_GMAIL_USERNAME', str),
                           'password': env('MERCURY_GMAIL_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('MERCURY_GMAIL_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = Gmail(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):

    subscription.config = {}
    d = Gmail(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    d = Gmail(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Mercury is on Gmail...enjoy') == 1


def test_connection(subscription):
    d = Gmail(subscription.channel)
    assert d.test_connection()
