# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from environ import Env
from pathlib import Path

from mercury.exceptions import PluginValidationError

from mercury_facebook import Facebook


env = Env(MERCURY_FACEBOOK_KEY='',
          MERCURY_FACEBOOK_PASSWORD='',
          MERCURY_FACEBOOK_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'key': env('MERCURY_FACEBOOK_KEY', str),
                           'password': env('MERCURY_FACEBOOK_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('MERCURY_FACEBOOK_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = Facebook(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):

    subscription.config = {}
    d = Facebook(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    d = Facebook(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Mercury is on Facebook...enjoy') == 1


def test_connection(subscription):
    d = Facebook(subscription.channel)
    assert d.test_connection()
