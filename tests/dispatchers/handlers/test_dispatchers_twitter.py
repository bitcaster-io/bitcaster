import os

import pytest

from bitcaster.dispatchers import Twitter
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_TWITTER_ACCOUNT')
@pytest.mark.django_db
class TestTwitterDispatcherTwitter(DispatcherBaseTest):
    TARGET = Twitter
    CONFIG = {'account': os.environ.get('TEST_TWITTER_ACCOUNT'),
              'consumer_key': os.environ.get('TEST_TWITTER_CONSUMER_KEY'),
              'consumer_secret': os.environ.get('TEST_TWITTER_CONSUMER_SECRET'),
              'access_token_key': os.environ.get('TEST_TWITTER_TOKEN_KEY'),
              'access_token_secret': os.environ.get('TEST_TWITTER_TOKEN_SECRET'),
              }
    RECIPIENT = os.environ.get('TEST_TWITTER_RECIPIENT')

    def test_get_recipient_address_alternative(self, dispatcher):
        dispatcher.get_recipient_address('@sax')
