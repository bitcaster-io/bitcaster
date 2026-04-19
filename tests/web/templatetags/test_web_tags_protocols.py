from typing import TYPE_CHECKING

from bitcaster.dispatchers.base import Capability
from bitcaster.web.templatetags.protocols import has

if TYPE_CHECKING:
    from bitcaster.models import Channel


def test_has(channel: "Channel") -> None:
    assert has(channel, Capability.TEXT)
