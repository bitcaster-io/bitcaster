import os
from unittest import mock
from unittest.mock import Mock

import pytest
from base_dispatchers import DispatcherBaseTest

from bitcaster.dispatchers import Hangout
from bitcaster.utils.tests.factories import ChannelFactory, SubscriptionFactory

pytestmark = pytest.mark.django_db


class Conn:
    def run(self):
        self.action(Mock())


@pytest.fixture(autouse=True)
def _django_db_marker(request):
    marker = request.node.get_closest_marker('skipif_missing')
    if marker:
        missing = [v for v in marker.args if v not in os.environ]
        if missing:
            pytest.skip(f"{','.join(missing)} not found in environment")


@pytest.mark.skipif_missing('TEST_HANGOUT_USER', 'TEST_HANGOUT_PASSWORD', 'TEST_HANGOUT_RECIPIENT')
class TestDispatcherHangout(DispatcherBaseTest):
    TARGET = Hangout
    CONFIG = {'username': 'username@gmail.com',
              'password': 'password',
              'sender': 'sender@sender.com'}
    RECIPIENT = 'aaa'

    @pytest.fixture()
    def dispatcher(self, application1):
        return Hangout(Mock(application=application1, config=self.CONFIG))

    @pytest.fixture()
    def subscription(self, dispatcher):
        return SubscriptionFactory(channel=ChannelFactory(handler=dispatcher))

    def test_get_connection(self, dispatcher, subscription):
        with mock.patch('%s.FireAndForget' % dispatcher.__module__):
            assert dispatcher._get_connection()

    def test_emit(self, dispatcher, subscription):
        with mock.patch('%s.Message' % dispatcher.__module__):
            with mock.patch('%s.JID' % dispatcher.__module__):
                with mock.patch.object(dispatcher, '_get_connection', side_effect=[Conn()]):
                    assert dispatcher.emit(subscription, '', '')

    def test_test_connection(self, dispatcher, subscription):
        with mock.patch('%s.JID' % dispatcher.__module__):
            with mock.patch.object(dispatcher, '_get_connection', side_effect=[Conn()]):
                assert dispatcher.test_connection()
