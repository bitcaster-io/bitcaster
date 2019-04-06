import os

import pytest

from bitcaster.dispatchers import Telegram
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_TELEGRAM_CHAT_ID')
@pytest.mark.django_db
class TestDispatcherTelegram(DispatcherBaseTest):
    TARGET = Telegram
    CONFIG = {'bot_name': os.environ.get('TEST_TELEGRAM_BOT_NAME'),
              'bot_token': os.environ.get('TEST_TELEGRAM_BOT_TOKEN'),
              }
    RECIPIENT = os.environ.get('TEST_TELEGRAM_RECIPIENT')
