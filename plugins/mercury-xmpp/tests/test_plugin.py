# -*- coding: utf-8 -*-
from unittest.mock import Mock

import pytest
from environ import Env
from pathlib import Path

from mercury.exceptions import PluginValidationError

from mercury_xmpp import Xmpp
import vcr as _vcr

env = Env(MERCURY_XMPP_USERNAME='',
          MERCURY_XMPP_PASSWORD='',
          MERCURY_XMPP_RECIPIENT='',
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
    # filter_headers=['authorization'],
    # filter_query_parameters=['mail', 'pass'],
    # filter_post_data_parameters=['mail', 'pass'],
    # before_record_request=before_record_cb,
)


@pytest.fixture
def subscription():
    application = Mock()
    user = Mock()
    channel = Mock(application=application,
                   config={'username': env('MERCURY_XMPP_USERNAME', str),
                           'password': env('MERCURY_XMPP_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('MERCURY_XMPP_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = Xmpp(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):
    subscription.config = {}
    d = Xmpp(subscription.channel)
    with pytest.raises(PluginValidationError):
        d.validate_subscription(subscription)


def test_send(subscription, monkeypatch):
    monkeypatch.setattr('django.contrib.sites.models.Site', Mock(id=1))
    with vcr.use_cassette('test_send.yaml'):
        d = Xmpp(subscription.channel)
        assert d.emit(subscription,
                      'subject',
                      'Mercury is on Xmpp...enjoy') == 1


def test_connection(subscription, monkeypatch):
    monkeypatch.setattr('django.contrib.sites.models.Site', Mock(id=1))
    with vcr.use_cassette('test_connection.yaml'):
        d = Xmpp(subscription.channel)
        assert d.test_connection()
