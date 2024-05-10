import factory
from factory import Sequence

from bitcaster.models import Event

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory


class EventFactory(AutoRegisterModelFactory):
    name = Sequence(lambda n: "Event-%03d" % n)
    application = factory.SubFactory(ApplicationFactory)

    class Meta:
        model = Event
        django_get_or_create = ("name",)

    @factory.post_generation
    def channels(dist: "Event", create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for ch in extracted:
                dist.channels.add(ch)

    @factory.post_generation
    def messages(dist: "Event", create, extracted, **kwargs):
        from .message import MessageFactory

        if not create:
            return

        if extracted:
            if isinstance(extracted, int):
                for _ in range(extracted):
                    msg = MessageFactory()
                    dist.messages.add(msg)
                    dist.channels.add(msg.channel)
            else:
                for msg in extracted:
                    dist.messages.add(msg)
                    dist.channels.add(msg.channel)
