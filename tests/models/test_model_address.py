from typing import Any

import pytest

from bitcaster.constants import AddressType
from bitcaster.models import Address, Channel


def test_manager_valid(address: "Address", channel: "Channel") -> None:
    assert not Address.objects.valid()
    address.validate_channel(channel)
    assert Address.objects.valid()


def test_address(db: Any) -> None:
    from testutils.factories import AddressFactory, ChannelFactory

    addr: "Address" = AddressFactory()
    ch: "Channel" = ChannelFactory()
    addr.validate_channel(ch)

    assert list(addr.channels.all()) == [ch]


@pytest.mark.parametrize(
    "value,type_",
    [
        ("test@example.com", AddressType.EMAIL),
        ("+1 (817) 943-8393", AddressType.PHONE),
        ("acount", AddressType.ACCOUNT),
    ],
)
def test_save(value: str, type_: AddressType) -> None:
    from testutils.factories import AddressFactory, ChannelFactory

    addr: "Address" = AddressFactory()
    ch: "Channel" = ChannelFactory()
    addr.validate_channel(ch)

    assert list(addr.channels.all()) == [ch]
