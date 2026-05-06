from typing import Any, cast

import uuid

import factory
from factory import Sequence

from testutils.dispatcher import XDispatcher

from strategy_field.utils import fqn

from bitcaster.models import Channel

from .base import AutoRegisterModelFactory
from .org import OrganizationFactory, ProjectFactory


class ChannelFactory(AutoRegisterModelFactory[Channel]):
    name = Sequence(lambda n: "Channel-%03d" % n)
    project = factory.SubFactory(ProjectFactory)
    organization = factory.SelfAttribute("project.organization")
    dispatcher = fqn(XDispatcher)
    config = factory.LazyFunction(lambda: {"seed": uuid.uuid4().hex})

    class Meta:
        model = Channel
        django_get_or_create = ("name", "organization", "project")

    @classmethod
    def create(cls, **kwargs: dict[str, Any]) -> Channel:
        if kwargs.get("project"):
            kwargs["organization"] = kwargs["project"].organization  # type: ignore[attr-defined]
        if not kwargs.get("organization"):
            kwargs["organization"] = OrganizationFactory.create()

        if "project" not in kwargs:
            kwargs["project"] = ProjectFactory.create(organization=kwargs["organization"])

        return cast("Channel", super().create(**kwargs))
