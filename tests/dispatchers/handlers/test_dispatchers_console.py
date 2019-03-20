import pytest

from bitcaster.dispatchers import ConsoleDispatcher
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


class TestDispatcherGmail(DispatcherBaseTest):
    TARGET = ConsoleDispatcher
    CONFIG = {}
    RECIPIENT = 'unused'
