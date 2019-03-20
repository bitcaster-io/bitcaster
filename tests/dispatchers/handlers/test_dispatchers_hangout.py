import os
from unittest.mock import Mock

import pytest

from bitcaster.dispatchers import Hangout
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

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
