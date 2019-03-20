import os

import pytest

from bitcaster.dispatchers import Skype
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_SKYPE_ACCOUNT', 'TEST_SKYPE_PASSWORD')
@pytest.mark.django_db
class TestDispatcherSkype(DispatcherBaseTest):
    TARGET = Skype
    CONFIG = {'username': os.environ.get('TEST_SKYPE_ACCOUNT'),
              'password': os.environ.get('TEST_SKYPE_PASSWORD')}
    RECIPIENT = os.environ.get('TEST_SKYPE_RECIPIENT')
