import os

import pytest

from bitcaster.dispatchers import TwilioWhatsApp
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_TWILIO_WA_SID')
@pytest.mark.django_db
class TestDispatcherTwilioWhatsApp(DispatcherBaseTest):
    TARGET = TwilioWhatsApp
    CONFIG = {'sid': os.environ.get('TEST_TWILIO_WA_SID'),
              'token': os.environ.get('TEST_TWILIO_WA_TOKEN'),
              'sender': os.environ.get('TEST_TWILIO_WA_SENDER'),
              }
    RECIPIENT = os.environ.get('TEST_TWILIO_WA_RECIPIENT')

    @pytest.mark.paid
    def test_emit(self, dispatcher, subscription):
        super().test_emit(dispatcher, subscription)
