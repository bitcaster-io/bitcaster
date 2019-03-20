import os

import pytest

from bitcaster.dispatchers import SlackWebhook
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_SLACK_URL')
@pytest.mark.django_db
class TestDispatcherSlackWebhook(DispatcherBaseTest):
    TARGET = SlackWebhook
    CONFIG = {'url': os.environ.get('TEST_SLACK_URL')}
    RECIPIENT = os.environ.get('TEST_SLACK_RECIPIENT')
