from django import template

from bitcaster.dispatchers.base import Capability, MessageProtocol
from bitcaster.models import Channel

register = template.Library()

#
# @register.filter(name="int")
# def integer(obj):
#     return int(obj)
#
#
# @register.simple_tag
# def setvar(val):
#     return val


@register.filter
def has(ch: Channel, capability: Capability) -> bool:
    return MessageProtocol[ch.protocol].has_capability(capability)
