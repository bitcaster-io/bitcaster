from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import Channel, Message


def test_instantiate(message: "Message", channel: "Channel"):
    m = message.clone(channel)
    assert m.channel == channel
    assert m.event == message.event
    assert m.id != message.id
