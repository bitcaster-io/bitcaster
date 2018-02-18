# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from mercury_plivo import Plivo
from environ import Env
from pathlib import Path
import vcr as _vcr

from mercury.exceptions import PluginValidationError

env = Env(MERCURY_PLIVO_SID='',
          MERCURY_PLIVO_TOKEN='',
          MERCURY_PLIVO_RECIPIENT='',
          MERCURY_PLIVO_SENDER='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


def before_record_cb(request):
    if request.path == '/login.php':
        request.body = "<removed>"
    return request


vcr = _vcr.VCR(
    serializer='yaml',
    cassette_library_dir=str(Path(__file__).parent / 'cassettes'),
    record_mode='always',
    match_on=['uri', 'method'],
    # use these to clear sensitive data
    filter_headers=['authorization'],
    # filter_query_parameters=['mail', 'pass'],
    # filter_post_data_parameters=['mail', 'pass'],
    before_record_request=before_record_cb,
)


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'sid': env('MERCURY_PLIVO_SID', str),
                           'token': env('MERCURY_PLIVO_TOKEN', str),
                           'sender': env('MERCURY_PLIVO_SENDER', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('MERCURY_PLIVO_RECIPIENT', str)},
                channel=channel)


def test_validate_config(subscription):
    d = Plivo.options_class(data=subscription.channel.config)
    assert d.is_valid(), d.errors


def test_validate_subscription(subscription):
    d = Plivo(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):
    subscription.config = {}
    d = Plivo(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    with vcr.use_cassette('test_send.yaml'):
        d = Plivo(subscription.channel)
        assert d.emit(subscription, 'subject', 'message') == 1


def test_connection(subscription):
    with vcr.use_cassette('test_connection.yaml'):
        d = Plivo(subscription.channel)
        assert d.test_connection()
