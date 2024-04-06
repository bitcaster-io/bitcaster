import factory
from factory import Sequence
from factory.django import DjangoModelFactory

from bitcaster.models.message import Message

from .channel import ChannelFactory
from .event import EventTypeFactory


class MessageFactory(DjangoModelFactory):
    name = Sequence(lambda n: "Message-%03d" % n)
    channel = factory.SubFactory(ChannelFactory)
    event = factory.SubFactory(EventTypeFactory)
    content = "Message for {{ event.name }} on channel {{channel.name}}"

    class Meta:
        model = Message
        django_get_or_create = ("name",)
