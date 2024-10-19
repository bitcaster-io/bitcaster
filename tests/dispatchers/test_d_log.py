from typing import TYPE_CHECKING

import pytest
from strategy_field.utils import fqn

from bitcaster.dispatchers.log import BitcasterSysDispatcher
from bitcaster.models import Channel

if TYPE_CHECKING:
    from bitcaster.dispatchers.base import Payload

pytestmark = [pytest.mark.dispatcher, pytest.mark.django_db]


def test_log(mail_payload: "Payload") -> None:
    ch = Channel(dispatcher=fqn(BitcasterSysDispatcher), config={})

    assert BitcasterSysDispatcher(ch).send("123456", mail_payload)
