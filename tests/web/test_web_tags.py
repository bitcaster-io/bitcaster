from bitcaster.dispatchers.base import Capability
from bitcaster.models import Channel
from bitcaster.web.templatetags.protocols import has


def test_has(channel: "Channel") -> None:
    assert has(channel, Capability.TEXT)
