from unittest import mock
from unittest.mock import Mock

import pytest

from bitcaster.dispatchers import Email
from bitcaster.utils.tests.factories import ChannelFactory, SubscriptionFactory

pytestmark = pytest.mark.django_db


@pytest.fixture()
def dispatcher(application1):
    return Email(Mock(application=application1, config={'server': 'server',
                                                        'sender': 'sender@sender.com'}))


@pytest.fixture()
def subscription(dispatcher):
    return SubscriptionFactory(channel=ChannelFactory(handler=dispatcher))


def test_base():
    base = Email()
    assert base


def test_get_options_form(dispatcher):
    assert dispatcher.get_options_form()
    assert dispatcher.get_options_form(data={'abc': 11})


def test_validate_configuration(dispatcher):
    assert dispatcher.validate_configuration({'server': 'server',
                                              'sender': 'sender@example.com'})


def test_get_recipient_address(dispatcher):
    subscription = SubscriptionFactory()
    assert dispatcher.get_recipient_address(subscription)
    assert dispatcher.get_recipient_address('sender@example.com')


def test_emit(dispatcher, subscription):
    with mock.patch.object(dispatcher, '_get_connection'):
        assert dispatcher.emit(subscription, '', '')


def test_test_connection(dispatcher, subscription):
    with mock.patch.object(dispatcher, '_get_connection'):
        assert dispatcher.test_connection()


def test_get_usage(dispatcher):
    assert dispatcher.get_usage()
    assert dispatcher.get_usage_message()


def test_validate_address(dispatcher):
    assert dispatcher.validate_address('sender@example.com')


def test_validate_subscription(dispatcher, subscription):
    assert dispatcher.validate_subscription(subscription)
    assert dispatcher.validate_subscription('sender@example.com')


def test_validate_message(dispatcher):
    assert dispatcher.validate_message('message')


def test_fqn(dispatcher):
    assert dispatcher.fqn
