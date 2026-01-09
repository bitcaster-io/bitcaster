from typing import Any, cast

import factory
from factory import Sequence

from bitcaster.models import MessageTemplate

from .base import AutoRegisterModelFactory
from .channel import ChannelFactory
from .event import EventFactory
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory


class MessageFactory(AutoRegisterModelFactory[MessageTemplate]):
    name = Sequence(lambda n: "Message-%03d" % n)
    content = "Message for {{ event.name }} on channel {{channel.name}}"

    organization = factory.SubFactory(OrganizationFactory)
    project = factory.SubFactory(ProjectFactory)
    application = factory.SubFactory(ApplicationFactory)
    channel = factory.SubFactory(ChannelFactory)
    event = factory.SubFactory(EventFactory)

    class Meta:
        model = MessageTemplate
        django_get_or_create = ("name", "organization", "channel", "event")

    @classmethod
    def create(cls, **kwargs: Any) -> MessageTemplate:
        if kwargs.get("event"):
            kwargs["organization"] = kwargs["event"].application.project.organization

        if not kwargs.get("organization"):
            kwargs["organization"] = OrganizationFactory()

        return cast("MessageTemplate", super().create(**kwargs))
