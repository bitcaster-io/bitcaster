import os
from unittest.mock import Mock

import pytest
from base_dispatchers import DispatcherBaseTest

from bitcaster.dispatchers import Hangout

pytestmark = pytest.mark.django_db


class Conn:
    def run(self):
        self.action(Mock())


@pytest.mark.skipif_missing('TEST_HANGOUT_USER', 'TEST_HANGOUT_PASSWORD', 'TEST_HANGOUT_RECIPIENT')
class TestDispatcherHangout(DispatcherBaseTest):
    TARGET = Hangout
    CONFIG = {'username': os.environ.get('TEST_HANGOUT_USER'),
              'password': os.environ.get('TEST_HANGOUT_PASSWORD'),
              'sender': 'sender@sender.com'}
    RECIPIENT = os.environ.get('TEST_HANGOUT_RECIPIENT')

    # def test_get_connection(self, dispatcher, subscription):
    #     with mock.patch('%s.FireAndForget' % dispatcher.__module__):
    #         assert dispatcher._get_connection()
    #
    # def test_emit(self, dispatcher, subscription):
    #     with mock.patch('%s.Message' % dispatcher.__module__):
    #         with mock.patch('%s.JID' % dispatcher.__module__):
    #             with mock.patch.object(dispatcher, '_get_connection', side_effect=[Conn()]):
    #                 assert dispatcher.emit(subscription, '', '')
    #
    # def test_test_connection(self, dispatcher, subscription):
    #     with mock.patch('%s.JID' % dispatcher.__module__):
    #         with mock.patch.object(dispatcher, '_get_connection', side_effect=[Conn()]):
    #             assert dispatcher.test_connection()
