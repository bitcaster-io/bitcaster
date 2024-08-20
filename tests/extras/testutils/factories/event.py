from typing import TYPE_CHECKING, Any

import factory
from factory import Sequence

from bitcaster.models import Event

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory

if TYPE_CHECKING:
    from bitcaster.models import Channel


class EventFactory(AutoRegisterModelFactory[Event]):
    name = Sequence(lambda n: "Event-%03d" % n)
    application = factory.SubFactory(ApplicationFactory)

    class Meta:
        model = Event
        django_get_or_create = ("name",)

    @factory.post_generation
    def channels(self: "Event", create: bool, extracted: "list[Channel]", **kwargs):
        if not create:
            return

        if extracted:
            for ch in extracted:
                self.channels.add(ch)

    @factory.post_generation
    def messages(self: "Event", create: bool, extracted: Any, **kwargs: Any) -> None:
        from .message import MessageFactory

        if not create:
            return

        if extracted:
            if isinstance(extracted, int):
                for _ in range(extracted):
                    msg = MessageFactory()
                    self.messages.add(msg)
                    self.channels.add(msg.channel)
            else:
                for msg in extracted:
                    self.messages.add(msg)
                    self.channels.add(msg.channel)
