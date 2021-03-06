import os

import pytest

from bitcaster.dispatchers import Twilio
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_TWILIO_SID')
@pytest.mark.django_db
class TestDispatcherTwilio(DispatcherBaseTest):
    TARGET = Twilio
    CONFIG = {'sid': os.environ.get('TEST_TWILIO_SID'),
              'token': os.environ.get('TEST_TWILIO_TOKEN'),
              'sender': os.environ.get('TEST_TWILIO_SENDER'),
              }
    RECIPIENT = os.environ.get('TEST_TWILIO_RECIPIENT')

    @pytest.mark.paid
    def test_emit(self, dispatcher, subscription):
        super().test_emit(dispatcher, subscription)
