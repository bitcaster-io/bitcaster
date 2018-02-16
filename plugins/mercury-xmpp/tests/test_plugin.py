# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
import pytest
from environ import Env
from pathlib import Path

from mercury.exceptions import PluginValidationError

from mercury_xmpp import Xmpp


env = Env(MERCURY_XMPP_USERNAME='',
          MERCURY_XMPP_XMPP_PASSWORD='',
          MERCURY_XMPP_XMPP_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'username': env('MERCURY_XMPP_USERNAME', str),
                           'password': env('MERCURY_XMPP_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('MERCURY_XMPP_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = Xmpp(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):

    subscription.config = {}
    d = Xmpp(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    d = Xmpp(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Mercury is on Xmpp...enjoy') == 1


def test_connection(subscription):
    d = Xmpp(subscription.channel)
    assert d.test_connection()
