from typing import Any

import factory
from factory import Sequence

from bitcaster.models import Message

from .base import AutoRegisterModelFactory
from .channel import ChannelFactory
from .event import EventFactory
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory


class MessageFactory(AutoRegisterModelFactory[Message]):
    name = Sequence(lambda n: "Message-%03d" % n)
    content = "Message for {{ event.name }} on channel {{channel.name}}"

    organization = factory.SubFactory(OrganizationFactory)
    project = factory.SubFactory(ProjectFactory)
    application = factory.SubFactory(ApplicationFactory)
    channel = factory.SubFactory(ChannelFactory)
    event = factory.SubFactory(EventFactory)

    class Meta:
        model = Message
        django_get_or_create = ("name", "organization", "channel", "event")

    @classmethod
    def create(cls, **kwargs: Any) -> Message:
        if kwargs.get("event", None):
            kwargs["organization"] = kwargs["event"].application.project.organization

        if not kwargs.get("organization", None):
            kwargs["organization"] = OrganizationFactory()

        return super().create(**kwargs)
