import factory
from factory import Sequence

from bitcaster.models import Message

from .base import AutoRegisterModelFactory
from .channel import ChannelFactory
from .event import EventFactory
from .org import OrganizationFactory


class MessageFactory(AutoRegisterModelFactory):
    name = Sequence(lambda n: "Message-%03d" % n)
    content = "Message for {{ event.name }} on channel {{channel.name}}"

    organization = factory.SubFactory(OrganizationFactory)
    channel = factory.SubFactory(ChannelFactory)
    event = factory.SubFactory(EventFactory)

    class Meta:
        model = Message
        django_get_or_create = ("name",)
