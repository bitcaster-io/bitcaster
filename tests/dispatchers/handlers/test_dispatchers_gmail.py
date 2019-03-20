import os

import pytest

from bitcaster.dispatchers import Gmail
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_GMAIL_USER', 'TEST_GMAIL_PASSWORD', 'TEST_GMAIL_RECIPIENT')
class TestDispatcherGmail(DispatcherBaseTest):
    TARGET = Gmail
    CONFIG = {'username': os.environ.get('TEST_GMAIL_USER'),
              'password': os.environ.get('TEST_GMAIL_PASSWORD'),
              'sender': 'sender@sender.com'}
    RECIPIENT = os.environ.get('TEST_GMAIL_RECIPIENT')
