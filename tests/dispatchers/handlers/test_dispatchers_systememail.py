import os

import pytest
from constance.test import override_config

from bitcaster.dispatchers import SystemEmail
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def setup_config():
    config = override_config(
        EMAIL_HOST=os.environ.get('TEST_EMAIL_HOST', 'smtp.gmail.com'),
        EMAIL_HOST_PORT=os.environ.get('TEST_EMAIL_PORT', '587'),
        EMAIL_HOST_USER=os.environ.get('TEST_EMAIL_USER'),
        EMAIL_HOST_PASSWORD=os.environ.get('TEST_EMAIL_PASSWORD'),
        EMAIL_USE_TLS=os.environ.get('TEST_EMAIL_TLS', '1'),
    )
    config.enable()
    yield
    config.disable()


@pytest.mark.skipif_missing('TEST_EMAIL_USER', 'TEST_EMAIL_PASSWORD', 'TEST_EMAIL_RECIPIENT')
@pytest.mark.django_db
class TestDispatcherSystemEmail(DispatcherBaseTest):
    TARGET = SystemEmail
    CONFIG = {'username': os.environ.get('TEST_EMAIL_USER'),
              'password': os.environ.get('TEST_EMAIL_PASSWORD'),
              'server': os.environ.get('TEST_EMAIL_HOST', 'smtp.gmail.com'),
              'port': os.environ.get('TEST_EMAIL_PORT', '587'),
              'tls': os.environ.get('TEST_EMAIL_TLS', '1'),
              'sender': 'sender@sender.com'}
    RECIPIENT = os.environ.get('TEST_EMAIL_RECIPIENT')
