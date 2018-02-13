# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
from environ import Env
from mercury.exceptions import PluginValidationError

from mercury_skype import Skype

env = Env(MERCURY_SKYPE_USERNAME='',
          MERCURY_SKYPE_PASSWORD='',
          MERCURY_SKYPE_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'username': env('MERCURY_SKYPE_USERNAME', str),
                           'password': env('MERCURY_SKYPE_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('MERCURY_SKYPE_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    from mercury_skype import Skype
    d = Skype(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):

    subscription.config = {}
    d = Skype(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    d = Skype(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Mercury is on Skype...enjoy') == 1


def test_connection(subscription):
    d = Skype(subscription.channel)
    assert d.test_connection()
