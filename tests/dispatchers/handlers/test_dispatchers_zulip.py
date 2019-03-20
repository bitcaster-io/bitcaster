import os

import pytest

from bitcaster.dispatchers import ZulipPrivate
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_ZULIP_SITE', 'TEST_ZULIP_KEY', 'TEST_ZULIP_EMAIL')
@pytest.mark.django_db
class TestDispatcherTwitter(DispatcherBaseTest):
    TARGET = ZulipPrivate
    CONFIG = {'site': os.environ.get('TEST_ZULIP_SITE'),
              'key': os.environ.get('TEST_ZULIP_KEY'),
              'email': os.environ.get('TEST_ZULIP_EMAIL'),
              }
    RECIPIENT = os.environ.get('TEST_ZULIP_RECIPIENT')
