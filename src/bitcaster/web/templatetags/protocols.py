from django import template

from bitcaster.dispatchers.base import Capability, MessageProtocol
from bitcaster.models import Channel

register = template.Library()


@register.filter
def has(ch: Channel, capability: Capability) -> bool:
    return MessageProtocol[ch.protocol].has_capability(capability)
