# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from environ import Env
from pathlib import Path

from mercury.exceptions import PluginValidationError

from mercury_gmail import Gmail
import vcr as _vcr

env = Env(MERCURY_GMAIL_USERNAME='',
          MERCURY_GMAIL_PASSWORD='',
          MERCURY_GMAIL_RECIPIENT='',
          MERCURY_GMAIL_SENDER='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


def before_record_cb(request):
    if request.path == '/login.php':
        request.body = "<removed>"
    return request


vcr = _vcr.VCR(
    serializer='yaml',
    cassette_library_dir=str(Path(__file__).parent / 'cassettes'),
    record_mode='once',
    match_on=['uri', 'method'],
    # filter_headers=['authorization'],
    # filter_query_parameters=['mail', 'pass'],
    # filter_post_data_parameters=['mail', 'pass'],
    before_record_request=before_record_cb,
    # sensitive HTTP request goes here
)


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock(email=env('MERCURY_GMAIL_RECIPIENT', str))
    channel = Mock(application=application,
                   config={'username': env('MERCURY_GMAIL_USERNAME', str),
                           'password': env('MERCURY_GMAIL_PASSWORD', str),
                           'sender': env('MERCURY_GMAIL_SENDER', str),
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
    d = Gmail(subscription.channel)
    subscription.subscriber.email = ''
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription, settings):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    d = Gmail(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Mercury is on Gmail...enjoy') == 1


def test_connection(subscription):
    d = Gmail(subscription.channel)
    assert d.test_connection()
