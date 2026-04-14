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
        ("+18179438393", AddressType.PHONE),
        ("acount", AddressType.ACCOUNT),
    ],
)
def test_save(db: Any, value: str, type_: AddressType) -> None:
    from testutils.factories import AddressFactory, UserFactory

    user = UserFactory()
    addr = AddressFactory(user=user, value=value)
    # The save() method calls get_type_from_value
    # account type might be generic if not email/phone
    if type_ == AddressType.ACCOUNT:
        assert addr.type == AddressType.GENERIC
    else:
        assert addr.type == type_


def test_natural_key(address: "Address") -> None:
    assert address.natural_key() == (address.user.username, address.name)


def test_get_by_natural_key(address: "Address") -> None:
    username, name = address.natural_key()
    assert Address.objects.get_by_natural_key(username, name) == address
