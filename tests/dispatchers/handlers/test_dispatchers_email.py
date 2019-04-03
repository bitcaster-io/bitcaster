import os

import pytest

from bitcaster.dispatchers import Email
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.plugin
@pytest.mark.skipif_missing('TEST_EMAIL_USER', 'TEST_EMAIL_PASSWORD', 'TEST_EMAIL_RECIPIENT')
class TestDispatcherEmail(DispatcherBaseTest):
    TARGET = Email
    CONFIG = {'username': os.environ.get('TEST_EMAIL_USER'),
              'password': os.environ.get('TEST_EMAIL_PASSWORD'),
              'server': os.environ.get('TEST_EMAIL_HOST', 'smtp.gmail.com'),
              'port': os.environ.get('TEST_EMAIL_PORT', '587'),
              'tls': os.environ.get('TEST_EMAIL_TLS', '1'),
              'sender': 'sender@sender.com'}
    RECIPIENT = os.environ.get('TEST_EMAIL_RECIPIENT')
