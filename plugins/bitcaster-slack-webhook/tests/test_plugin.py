# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
import vcr as _vcr
from environ import Env

from bitcaster.exceptions import PluginValidationError
from bitcaster_slack_webhook import SlackWebhook

env = Env(BITCASTER_SLACK_WEBHOOK_URL='',
          BITCASTER_SLACK_WEBHOOK_RECIPIENT=''
          )

env.read_env(str(Path(__file__).parent / '.env'))


def before_record_request(request):
    original = str(request.body)
    for e in [env('BITCASTER_SLACK_WEBHOOK_URL', str)]:
        original = original.replace(e, '----')
    request.body = original.encode('utf8')

    original = request.uri
    for e in [env('BITCASTER_SLACK_WEBHOOK_URL', str)]:
        original = original.replace(e, '----')
    request.uri = original

    return request


def before_record_response(response):
    return response


vcr = _vcr.VCR(
    serializer='yaml',
    cassette_library_dir=str(Path(__file__).parent / 'cassettes'),
    record_mode='always',
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
                   config={'url': env('BITCASTER_SLACK_WEBHOOK_URL', str),
                           'bot_name': 'test',
                           'icon_url': 'http://google.com/',
                           })
    SlackWebhook.validate_configuration(channel.config)
    # SlackWebhook.validate_configuration()
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('BITCASTER_SLACK_WEBHOOK_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = SlackWebhook(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):
    subscription.config = {}
    d = SlackWebhook(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    # with vcr.use_cassette('test_send.yaml'):
    d = SlackWebhook(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Bitcaster is on SlackWebhook...enjoy') == 1


def test_connection(subscription):
    with vcr.use_cassette('test_connection.yaml'):
        d = SlackWebhook(subscription.channel)
        assert d.test_connection()
