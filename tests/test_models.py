from typing import TYPE_CHECKING, TypedDict

from testutils.factories.address import AddressFactory
from testutils.factories.channel import ChannelFactory
from testutils.factories.user import UserFactory
from testutils.factories.validation import ValidationFactory

if TYPE_CHECKING:
    from bitcaster.models import Address, ApiKey, Application, Channel, Event, Subscription, User

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "event": Event,
            "key": ApiKey,
            "channel": Channel,
            "subscription": Subscription,
        },
    )


def test_address(db):

    addr: "Address" = AddressFactory()
    ch: "Channel" = ChannelFactory()
    addr.validate_channel(ch)

    assert list(addr.channels.all()) == [ch]


def test_validation(db):

    v = ValidationFactory()

    ch: "Channel" = v.channel
    addr: "Address" = v.address

    assert list(addr.channels.all()) == [ch]


def test_user(db):

    u: "User" = UserFactory()
    addr: "Address" = u.addresses.create(value="test@example.com")

    assert list(u.addresses.all()) == [addr]
