from unittest.mock import Mock

import pytest

from bitcaster.models import Message
from bitcaster.utils.tests.factories import ChannelFactory, SubscriptionFactory

pytestmark = pytest.mark.django_db


@pytest.mark.incremental
class DispatcherBaseTest:
    CONFIG = None
    TARGET = None
    RECIPIENT = None

    @pytest.fixture()
    def dispatcher(self, application1):
        return self.TARGET(Mock(application=application1, config=self.CONFIG))

    @pytest.fixture()
    def subscription(self, dispatcher):
        return SubscriptionFactory(channel=ChannelFactory(handler=dispatcher),
                                   address=self.RECIPIENT)

    def test_create(self):
        base = self.TARGET(Mock())
        assert base

    def test_fqn(self, dispatcher):
        assert dispatcher.fqn

    def test_get_options_form(self, dispatcher):
        assert dispatcher.get_options_form()

    def test_get_options_form_param(self, dispatcher):
        assert dispatcher.get_options_form(data={'abc': 11})

    def test_validate_configuration(self, dispatcher):
        assert dispatcher.validate_configuration(self.CONFIG)

    def test_get_recipient_address(self, dispatcher, subscription):
        assert dispatcher.get_recipient_address(subscription)
        assert dispatcher.get_recipient_address(subscription.recipient)

    def test_emit(self, dispatcher, subscription):
        assert dispatcher.emit(subscription, 'test message', 'test subject')

    def test_test_connection(self, dispatcher, subscription):
        assert dispatcher.test_connection()

    def test_get_connection(self, dispatcher, subscription):
        assert dispatcher._get_connection()

    def test_get_usage(self, dispatcher):
        assert dispatcher.get_usage() is not None
        assert dispatcher.get_usage_message() is not None

    def test_validate_address(self, dispatcher, subscription):
        assert dispatcher.validate_address(subscription.recipient)

    def test_validate_subscription(self, dispatcher, subscription):
        assert dispatcher.validate_subscription(subscription)
        assert dispatcher.validate_subscription(subscription.recipient)

    def test_validate_message(self, dispatcher):
        assert dispatcher.validate_message(Message(body='message'))
