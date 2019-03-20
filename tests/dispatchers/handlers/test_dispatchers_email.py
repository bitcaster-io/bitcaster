from unittest import mock
from unittest.mock import Mock

import pytest
from base_dispatchers import DispatcherBaseTest

from bitcaster.dispatchers import Email
from bitcaster.utils.tests.factories import ChannelFactory, SubscriptionFactory

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_EMAIL_USER', 'TEST_EMAIL_PASSWORD', 'TEST_EMAIL_RECIPIENT')
class TestDispatcherEmail(DispatcherBaseTest):
    TARGET = Email
    CONFIG = {'server': 'server',
              'username': 'username',
              'password': 'password',
              'sender': 'sender@sender.com'}

    @pytest.fixture()
    def dispatcher(self, application1):
        return Email(Mock(application=application1, config=self.CONFIG))

    @pytest.fixture()
    def subscription(self, dispatcher):
        return SubscriptionFactory(channel=ChannelFactory(handler=dispatcher),
                                   address='tst@a.com',
                                   trigger_by=dispatcher.owner.application.organization.owner,
                                   subscriber=dispatcher.owner.application.organization.owner)

    def test_get_connection(self, dispatcher, subscription):
        with mock.patch('%s.get_connection' % dispatcher.__module__):
            assert dispatcher._get_connection()

    def test_validate_configuration(self, dispatcher):
        assert dispatcher.validate_configuration(self.CONFIG)

    def test_emit(self, dispatcher, subscription):
        with mock.patch.object(dispatcher, '_get_connection'):
            assert dispatcher.emit(subscription, '', '')

    def test_test_connection(self, dispatcher, subscription):
        with mock.patch.object(dispatcher, '_get_connection'):
            assert dispatcher.test_connection()
