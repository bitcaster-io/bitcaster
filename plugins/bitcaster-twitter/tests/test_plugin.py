# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
import vcr as _vcr
from environ import Env
from bitcaster_twitter import Twitter

env = Env(BITCASTER_TWITTER_CONSUMER_KEY='',
          BITCASTER_TWITTER_CONSUMER_SECRET='',
          BITCASTER_TWITTER_ACCESS_TOKEN_KEY='',
          BITCASTER_TWITTER_ACCESS_TOKEN_SECRET='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


def before_record_request(request):
    original = str(request.body)
    for e in [env('BITCASTER_TWITTER_CONSUMER_KEY', str),
              env('BITCASTER_TWITTER_CONSUMER_SECRET', str),
              env('BITCASTER_TWITTER_ACCESS_TOKEN_KEY', str),
              env('BITCASTER_TWITTER_ACCESS_TOKEN_SECRET', str)]:
        original = original.replace(e, "----")
    request.body = original.encode('utf8')

    original = request.uri
    for e in [env('BITCASTER_TWITTER_CONSUMER_KEY', str),
              env('BITCASTER_TWITTER_CONSUMER_SECRET', str),
              env('BITCASTER_TWITTER_ACCESS_TOKEN_KEY', str),
              env('BITCASTER_TWITTER_ACCESS_TOKEN_SECRET', str)]:
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
                   config={'consumer_key': env('BITCASTER_TWITTER_CONSUMER_KEY', str),
                           'consumer_secret': env('BITCASTER_TWITTER_CONSUMER_SECRET', str),
                           'access_token_key': env('BITCASTER_TWITTER_ACCESS_TOKEN_KEY', str),
                           'access_token_secret': env('BITCASTER_TWITTER_ACCESS_TOKEN_SECRET', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('BITCASTER_TWITTER_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = Twitter(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):

    subscription.config = {}
    d = Twitter(subscription.channel)
    d.validate_subscription(subscription)


def test_send(subscription):
    with vcr.use_cassette('test_send.yaml'):
        d = Twitter(subscription.channel)
        assert d.emit(subscription,
                      'subject',
                      'Bitcaster is on Twitter...enjoy') == 1


def test_connection(subscription):
    with vcr.use_cassette('test_connection.yaml'):
        d = Twitter(subscription.channel)
        assert d.test_connection()
