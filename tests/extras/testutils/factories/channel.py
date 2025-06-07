from typing import Any, cast

import factory
from factory import Sequence
from strategy_field.utils import fqn

from bitcaster.models import Channel
from testutils.dispatcher import XDispatcher

from .base import AutoRegisterModelFactory
from .org import OrganizationFactory, ProjectFactory


class ChannelFactory(AutoRegisterModelFactory[Channel]):
    name = Sequence(lambda n: "Channel-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    project = factory.SubFactory(ProjectFactory)
    dispatcher = fqn(XDispatcher)
    config = {"foo": "bar"}

    class Meta:
        model = Channel
        django_get_or_create = ("name", "organization", "project")

    @classmethod
    def create(cls, **kwargs: dict[str, Any]) -> Channel:
        if kwargs.get("project"):
            kwargs["organization"] = kwargs["project"].organization  # type: ignore[attr-defined]
        if not kwargs.get("organization"):
            kwargs["organization"] = OrganizationFactory()

        return cast("Channel", super().create(**kwargs))
