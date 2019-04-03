import os

import pytest

from bitcaster.dispatchers import Telegram
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_TELEGRAM_API_ID')
@pytest.mark.django_db
class TestDispatcherTelegram(DispatcherBaseTest):
    TARGET = Telegram
    CONFIG = {'api_id': os.environ.get('TEST_TELEGRAM_API_ID'),
              'api_hash': os.environ.get('TEST_TELEGRAM_API_HASH'),
              'title': os.environ.get('TEST_TELEGRAM_APP_TITLE'),
              'short_name': os.environ.get('TEST_TELEGRAM_SHORT_NAME'),
              'bot_token': os.environ.get('TEST_TELEGRAM_BOT_TOKEN'),
              'encryption_key': os.environ.get('TEST_TELEGRAM_ENCRYPTION_KEY'),
              }
    RECIPIENT = os.environ.get('TEST_TELEGRAM_RECIPIENT')

    def test_get_recipient_address_alternative(self, dispatcher):
        dispatcher.get_recipient_address('@sax')
