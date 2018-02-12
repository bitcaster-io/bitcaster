# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
import pytest
from environ import Env
from pathlib import Path

from mercury.exceptions import ValidationError

from mercury_{{cookiecutter.name}} import {{cookiecutter.classname}}


env = Env(MERCURY_{{cookiecutter.name|upper}}_USERNAME='',
          MERCURY_{{cookiecutter.name|upper}}_{{cookiecutter.name|upper}}_PASSWORD='',
          MERCURY_{{cookiecutter.name|upper}}_{{cookiecutter.name|upper}}_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'username': env('MERCURY_{{cookiecutter.name|upper}}_USERNAME', str),
                           'password': env('MERCURY_{{cookiecutter.name|upper}}_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('MERCURY_{{cookiecutter.name|upper}}_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = {{cookiecutter.classname}}(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):

    subscription.config = {}
    d = {{cookiecutter.classname}}(subscription.channel)
    with pytest.raises(ValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    d = {{cookiecutter.classname}}(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Mercury is on {{cookiecutter.classname}}...enjoy') == 1


def test_connection(subscription):
    d = {{cookiecutter.classname}}(subscription.channel)
    assert d.test_connection()
