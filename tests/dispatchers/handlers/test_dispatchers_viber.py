import os

import pytest

from bitcaster.dispatchers import Viber
from bitcaster.utils.tests.dispatcher_testcase import DispatcherBaseTest
from bitcaster.utils.tests.factories import ChannelFactory

pytestmark = pytest.mark.django_db


@pytest.mark.skipif_missing('TEST_VIBER_ACCOUNT', 'TEST_VIBER_SITE', 'TEST_VIBER_TOKEN', 'TEST_VIBER_RECIPIENT')
@pytest.mark.django_db
class TestDispatcherViber(DispatcherBaseTest):
    TARGET = Viber

    CONFIG = {
        'account_name': os.environ.get('TEST_VIBER_ACCOUNT'),
        'site': os.environ.get('TEST_VIBER_SITE'),
        'auth_token': os.environ.get('TEST_VIBER_TOKEN')
    }
    RECIPIENT = os.environ.get('TEST_VIBER_RECIPIENT')

    @pytest.fixture()
    def dispatcher(self, application1):
        ch = ChannelFactory(id=1, organization=application1.organization, handler=self.TARGET, config=self.CONFIG)
        # return self.TARGET(Mock(application=application1, config=self.CONFIG))
        return ch.handler
