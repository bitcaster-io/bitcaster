import pytest

from bitcaster.dispatchers import ConsoleDispatcher
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.plugin
class TestDispatcherConsole(DispatcherBaseTest):
    TARGET = ConsoleDispatcher
    CONFIG = {}
    RECIPIENT = 'unused'

    def test_misconfigured(self, application1):
        # ConsoleDispatcher does not have config
        pass
