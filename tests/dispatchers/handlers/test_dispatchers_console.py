import pytest
from base_dispatchers import DispatcherBaseTest

from bitcaster.dispatchers import ConsoleDispatcher

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_GMAIL_USER', 'TEST_GMAIL_PASSWORD', 'TEST_GMAIL_RECIPIENT')
class TestDispatcherGmail(DispatcherBaseTest):
    TARGET = ConsoleDispatcher
    CONFIG = {}
