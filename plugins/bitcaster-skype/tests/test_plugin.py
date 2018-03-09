# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
# import vcr as _vcr
from environ import Env

from bitcaster.exceptions import PluginValidationError, RecipientNotFound
from bitcaster_skype import Skype

env = Env(BITCASTER_SKYPE_USERNAME='',
          BITCASTER_SKYPE_PASSWORD='',
          BITCASTER_SKYPE_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


# def before_record_request(request):
#     if request.path == 'https://api.skype.com/users/self/profile':
#         request.body = "<removed>"
#     elif request.path == 'https://api.skype.com/users/self/profile':
#         request.body = "<removed>"
#     return request
#
#
# def before_record_response(response):
#     o = response['headers'].get('Set-Cookie', [])
#     for i, c in enumerate(o):
#         for e in [env('BITCASTER_SKYPE_USERNAME', str), env('BITCASTER_SKYPE_PASSWORD', str),
#                   env('BITCASTER_SKYPE_RECIPIENT', str)]:
#             if e in c:
#                 c = c.replace(e, "----")
#         o[i] = c
#     response['headers']['Set-Cookie'] = o
#
#     return response
#
#
# vcr = _vcr.VCR(
#     serializer='yaml',
#     cassette_library_dir=str(Path(__file__).parent / 'cassettes'),
#     record_mode='always',
#     match_on=['uri', 'method'],
#     filter_headers=['authorization', 'location', 'x-skypetoken'],
#     filter_query_parameters=['mail', 'pass', 'client_id'],
#     filter_post_data_parameters=['login', 'passwd'],
#     before_record_request=before_record_request,
#     before_record_response=before_record_response,
#     # sensitive HTTP request goes here
# )


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'username': env('BITCASTER_SKYPE_USERNAME', str),
                           'password': env('BITCASTER_SKYPE_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('BITCASTER_SKYPE_RECIPIENT', str)},
                channel=channel)


def test_validate_configuration(subscription):
    d = Skype.options_class(data=subscription.channel.config)
    assert d.is_valid(), d.errors


def test_validate_subscription(subscription):
    from bitcaster_skype import Skype
    d = Skype(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):
    subscription.config = {}
    d = Skype(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    d = Skype(subscription.channel)
    assert d.emit(subscription,
                  'subject',
                  'Bitcaster is on Skype...enjoy') == 1


def test_send_user_is_not_in_contactlist(subscription):
    subscription.config['recipient'] = 'abc'
    d = Skype(subscription.channel)
    with pytest.raises(RecipientNotFound):
        assert d.emit(subscription,
                      'subject',
                      'Bitcaster is on Skype...enjoy') == 1


def test_connection(subscription):
    d = Skype(subscription.channel)
    assert d.test_connection()
