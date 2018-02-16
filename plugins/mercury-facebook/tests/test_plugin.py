# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
import vcr as _vcr
from environ import Env
from mercury.exceptions import PluginValidationError

from mercury_facebook import Facebook

env = Env(MERCURY_FACEBOOK_KEY='',
          MERCURY_FACEBOOK_PASSWORD='',
          MERCURY_FACEBOOK_RECIPIENT='',
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
                   config={'key': env('MERCURY_FACEBOOK_KEY', str),
                           'password': env('MERCURY_FACEBOOK_PASSWORD', str),
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('MERCURY_FACEBOOK_RECIPIENT', str)},
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
    # monkeypatch.setattr('mercury_facebook.plugin.Client.login', Mock())
    with vcr.use_cassette('test_send.yaml'):
        d = Facebook(subscription.channel)
        assert d.emit(subscription,
                      'subject',
                      'Mercury is on Facebook...enjoy') == 1


def test_connection(subscription):
    with vcr.use_cassette('test_connection.yaml'):
        d = Facebook(subscription.channel)
        assert d.test_connection()
