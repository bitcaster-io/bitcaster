from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from bitcaster.models import Address, Channel, Validation


def test_validation(db):
    from testutils.factories import ValidationFactory

    v: "Validation" = ValidationFactory()

    ch: "Channel" = v.channel
    addr: "Address" = v.address

    assert list(addr.channels.all()) == [ch]


@pytest.mark.parametrize("args", [{}, {"application": None}, {"project": None, "application": None}])
def test_natural_key(args):
    from testutils.factories import ChannelFactory, Validation, ValidationFactory

    msg = ValidationFactory(channel=ChannelFactory(**args))
    assert Validation.objects.get_by_natural_key(*msg.natural_key()) == msg, msg.natural_key()
