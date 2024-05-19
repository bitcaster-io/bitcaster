import factory
from factory import Sequence
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

from bitcaster.models import Channel

from .base import AutoRegisterModelFactory
from .org import OrganizationFactory, ProjectFactory


class ChannelFactory(AutoRegisterModelFactory):
    name = Sequence(lambda n: "Channel-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    project = factory.SubFactory(ProjectFactory)
    dispatcher = fqn(TDispatcher)
    config = {"foo": "bar"}

    class Meta:
        model = Channel
        django_get_or_create = ("name", "organization", "project")

    @classmethod
    def create(cls, **kwargs):
        if kwargs.get("project", None):
            kwargs["organization"] = kwargs["project"].organization
        if not kwargs.get("organization", None):
            kwargs["organization"] = OrganizationFactory()

        return super().create(**kwargs)
