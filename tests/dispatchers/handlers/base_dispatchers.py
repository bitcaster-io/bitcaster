from unittest import mock
from unittest.mock import Mock

import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.incremental
class DispatcherBaseTest:
    CONFIG = None
    TARGET = None

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
        raise NotImplementedError

    def test_test_connection(self, dispatcher, subscription):
        with mock.patch.object(dispatcher, '_get_connection'):
            assert dispatcher.test_connection()

    def test_get_connection(self, dispatcher, subscription):
        raise NotImplementedError

    def test_get_usage(self, dispatcher):
        assert dispatcher.get_usage()
        assert dispatcher.get_usage_message()

    def test_validate_address(self, dispatcher, subscription):
        assert dispatcher.validate_address(subscription.recipient)

    def test_validate_subscription(self, dispatcher, subscription):
        assert dispatcher.validate_subscription(subscription)
        assert dispatcher.validate_subscription(subscription.recipient)

    def test_validate_message(self, dispatcher):
        assert dispatcher.validate_message('message')
