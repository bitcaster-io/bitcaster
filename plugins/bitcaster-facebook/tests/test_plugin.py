# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
import vcr as _vcr
from environ import Env

from bitcaster.exceptions import PluginValidationError
from bitcaster_facebook import Facebook

env = Env(BITCASTER_FACEBOOK_KEY='',
          BITCASTER_FACEBOOK_PASSWORD='',
          BITCASTER_FACEBOOK_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


def before_record_request(request):
    original = str(request.body)
    for e in [env('BITCASTER_FACEBOOK_KEY', str), env('BITCASTER_FACEBOOK_PASSWORD', str),
              env('BITCASTER_FACEBOOK_RECIPIENT', str)]:
        original = original.replace(e, "----")
    request.body = original.encode('utf8')

    original = request.uri
    for e in [env('BITCASTER_FACEBOOK_KEY', str), env('BITCASTER_FACEBOOK_PASSWORD', str),
              env('BITCASTER_FACEBOOK_RECIPIENT', str)]:
        original = original.replace(e, "----")
    request.uri = original

    return request


def before_record_response(response):
    return response


vcr = _vcr.VCR(
    serializer='yaml',
    cassette_library_dir=str(Path(__file__).parent / 'cassettes'),
    record_mode='once',
    match_on=['uri', 'method'],
    # use these to clear sensitive data
    filter_headers=['authorization'],
    filter_post_data_parameters=['From', 'To'],
    before_record_request=before_record_request,
    before_record_response=before_record_response,
)


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'key': env('BITCASTER_FACEBOOK_KEY', str),
                           'password': env('BITCASTER_FACEBOOK_PASSWORD', str),
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('BITCASTER_FACEBOOK_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = Facebook(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):
    subscription.config = {}
    d = Facebook(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription, monkeypatch):
    with vcr.use_cassette('test_send.yaml'):
        d = Facebook(subscription.channel)
        assert d.emit(subscription,
                      'subject',
                      'Bitcaster is on Facebook...enjoy') == 1


def test_connection(subscription, monkeypatch):
    with vcr.use_cassette('test_connection.yaml'):
        d = Facebook(subscription.channel)
        assert d.test_connection()
