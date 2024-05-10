from bitcaster.dispatchers.base import Capability
from bitcaster.web.templatetags.protocols import has


def test_has(channel):
    assert has(channel, Capability.TEXT)
