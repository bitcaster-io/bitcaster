# -*- coding: utf-8 -*-
from pathlib import Path
from unittest.mock import Mock

import pytest
import vcr as _vcr
from environ import Env
from bitcaster.exceptions import ValidationError
from {{cookiecutter.package_name}} import {{cookiecutter.classname}}

env = Env(BITCASTER_{{cookiecutter.package_name|upper}}_USERNAME='',
          BITCASTER_{{cookiecutter.package_name|upper}}_PASSWORD='',
          BITCASTER_{{cookiecutter.package_name|upper}}_RECIPIENT='',
          )

env.read_env(str(Path(__file__).parent / '.env'))


def before_record_request(request):
    original = str(request.body)
    for e in [env('BITCASTER_{{cookiecutter.package_name|upper}}_USERNAME', str),
              env('BITCASTER_{{cookiecutter.package_name|upper}}_PASSWORD', str),
              env('BITCASTER_{{cookiecutter.package_name|upper}}_RECIPIENT', str)]:
        original = original.replace(e, "----")
    request.body = original.encode('utf8')

    original = request.uri
    for e in [env('BITCASTER_{{cookiecutter.package_name|upper}}_USERNAME', str),
              env('BITCASTER_{{cookiecutter.package_name|upper}}_PASSWORD', str),
              env('BITCASTER_{{cookiecutter.package_name|upper}}_RECIPIENT', str)]:
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
                   config={'username': env('BITCASTER_{{cookiecutter.package_name|upper}}_USERNAME', str),
                           'password': env('BITCASTER_{{cookiecutter.package_name|upper}}_PASSWORD', str)
                           })
    event = Mock(application=application)

    return Mock(subscriber=user,
                event=event,
                config={'recipient': env('BITCASTER_{{cookiecutter.package_name|upper}}_RECIPIENT', str)},
                channel=channel)


def test_validate_subscription(subscription):
    d = {{cookiecutter.classname}}(subscription.channel)
    d.validate_subscription(subscription)


def test_validate_subscription_fail(subscription):

    subscription.config = {}
    d = {{cookiecutter.classname}}(subscription.channel)
    with pytest.raises(ValidationError):
        d.validate_subscription(subscription)


def test_send(subscription):
    with vcr.use_cassette('test_send.yaml'):
        d = {{cookiecutter.classname}}(subscription.channel)
        assert d.emit(subscription,
                      'subject',
                      'Bitcaster is on {{cookiecutter.classname}}...enjoy') == 1


def test_connection(subscription):
    with vcr.use_cassette('test_connection.yaml'):
        d = {{cookiecutter.classname}}(subscription.channel)
        assert d.test_connection()
