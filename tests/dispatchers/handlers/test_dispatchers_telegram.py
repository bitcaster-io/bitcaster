import os

import pytest

from bitcaster.dispatchers import TwitterDirectMessage, Telegram
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_TELEGRAM_ID')
@pytest.mark.django_db
class TestDispatcherTwitter(DispatcherBaseTest):
    TARGET = Telegram
    CONFIG = {'api_id': os.environ.get('TEST_TELEGRAM_ID'),
              'api_hash': os.environ.get('TEST_TELEGRAM_HASH'),
              'short_name': os.environ.get('TEST_TELEGRAM_SHORT_NAME'),
              'title': os.environ.get('TEST_TELEGRAM_TITLE'),
              }
    RECIPIENT = os.environ.get('TEST_TELEGRAM_RECIPIENT')
