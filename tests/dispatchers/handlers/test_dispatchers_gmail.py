from unittest import mock
from unittest.mock import Mock

import pytest

from bitcaster.dispatchers import Email
from bitcaster.utils.tests.factories import ChannelFactory, SubscriptionFactory
from test_dispatchers import DispatcherBaseTest

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("dispatcher","subscription")
class TestDispatcherEmail(DispatcherBaseTest):
    TARGET = Email

    @pytest.fixture()
    def dispatcher(self, application1):
        return Email(Mock(application=application1, config={'server': 'server',
                                                            'sender': 'sender@sender.com'}))

    @pytest.fixture()
    def subscription(self, dispatcher):
        return SubscriptionFactory(channel=ChannelFactory(handler=dispatcher))

    def test_get_connection(self, dispatcher, subscription):
        with mock.patch("%s.get_connection" % dispatcher.__module__):
            assert dispatcher._get_connection()
