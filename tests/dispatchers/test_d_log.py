import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers.log import BitcasterLogDispatcher
from bitcaster.models import Channel

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_log(mail_payload):
    ch = Channel(dispatcher=fqn(BitcasterLogDispatcher), config={})

    assert BitcasterLogDispatcher(ch).send("123456", mail_payload)
