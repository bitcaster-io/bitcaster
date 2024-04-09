from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from bitcaster.models import ApiKey, Application, Channel, EventType, Subscription, Address

    Context = TypedDict(
        "Context",
        {
            "app": Application,
            "event": EventType,
            "key": ApiKey,
            "channel": Channel,
            "subscription": Subscription,
        },
    )


def test_event(db):
    from testutils.factories import ValidationFactory

    v = ValidationFactory()

    ch: "Channel" = v.channel
    addr: "Address" = v.address

    assert list(addr.channels.all()) == [ch]
