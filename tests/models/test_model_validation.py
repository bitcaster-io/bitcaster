from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import Address, Channel, Validation


def test_validation(db):
    from testutils.factories import ValidationFactory

    v: "Validation" = ValidationFactory()

    ch: "Channel" = v.channel
    addr: "Address" = v.address

    assert list(addr.channels.all()) == [ch]
