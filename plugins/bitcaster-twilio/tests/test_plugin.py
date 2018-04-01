# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
import vcr as _vcr
from bitcaster_twilio import Twilio
from environ import Env, json

from bitcaster.exceptions import PluginValidationError

env = Env(BITCASTER_TWILIO_SID='',
          BITCASTER_TWILIO_TOKEN='',
          BITCASTER_TWILIO_SENDER='',
          BITCASTER_TWILIO_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


def before_record_request(request):
    original = str(request.body)
    for e in [env('BITCASTER_TWILIO_SID', str), env('BITCASTER_TWILIO_SENDER', str),
              env('BITCASTER_TWILIO_RECIPIENT', str)]:
        original = original.replace(e, "----")
    request.body = original.encode('utf8')

    original = request.uri
    for e in [env('BITCASTER_TWILIO_SID', str), env('BITCASTER_TWILIO_SENDER', str),
              env('BITCASTER_TWILIO_RECIPIENT', str)]:
        original = original.replace(e, "----")
    request.uri = original

    return request


def before_record_response(response):
    original = json.loads(response["body"]["string"])
    for key in ['to', 'from', 'account_sid', 'media', 'uri']:
        original[key] = '----'

    response["body"]["string"] = json.dumps(original).encode('utf8')
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
                   config={'sid': env('BITCASTER_TWILIO_SID', str),
                           'token': env('BITCASTER_TWILIO_TOKEN', str),
                           'sender': env('BITCASTER_TWILIO_SENDER', str),
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('BITCASTER_TWILIO_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = Twilio(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):
    subscription.config = {}
    d = Twilio(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription, monkeypatch):
    with vcr.use_cassette('test_send.yaml'):
        d = Twilio(subscription.channel)
        assert d.emit(subscription, 'subject', 'message') == 1


def test_connection(subscription, monkeypatch):
    with vcr.use_cassette('test_connection.yaml'):
        d = Twilio(subscription.channel)
        assert d.test_connection()
