# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
import vcr as _vcr
from environ import Env

from bitcaster.exceptions import PluginValidationError
from bitcaster_hangout import Hangout

env = Env(BITCASTER_HANGOUT_USERNAME='',
          BITCASTER_HANGOUT_PASSWORD='',
          BITCASTER_HANGOUT_RECIPIENT='',
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
    user = Mock()
    channel = Mock(application=application,
                   config={'username': env('BITCASTER_HANGOUT_USERNAME', str),
                           'password': env('BITCASTER_HANGOUT_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('BITCASTER_HANGOUT_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = Hangout(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):
    subscription.config = {}
    d = Hangout(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription, monkeypatch):
    monkeypatch.setattr('bitcaster_hangout.plugin.Client', Mock())
    d = Hangout(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Bitcaster is on Hangout...enjoy') == 1


def test_connection(subscription, monkeypatch):
    d = Hangout(subscription.channel)
    assert d.test_connection()
