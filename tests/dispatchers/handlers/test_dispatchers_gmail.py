from unittest import mock
from unittest.mock import Mock

import pytest
from base_dispatchers import DispatcherBaseTest

from bitcaster.dispatchers import Email
from bitcaster.utils.tests.factories import ChannelFactory, SubscriptionFactory

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('dispatcher', 'subscription')
class TestDispatcherGmail(DispatcherBaseTest):
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
        return SubscriptionFactory(channel=ChannelFactory(handler=dispatcher))

    def test_get_connection(self, dispatcher, subscription):
        with mock.patch('%s.get_connection' % dispatcher.__module__):
            assert dispatcher._get_connection()

    def test_emit(self, dispatcher, subscription):
        with mock.patch.object(dispatcher, '_get_connection'):
            assert dispatcher.emit(subscription, '', '')
