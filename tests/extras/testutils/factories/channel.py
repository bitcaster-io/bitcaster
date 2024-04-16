import factory
from factory import Sequence
from strategy_field.utils import fqn
from testutils.dispatcher import TestDispatcher

from bitcaster.models import Channel

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory


class ChannelFactory(AutoRegisterModelFactory):
    class Meta:
        model = Channel
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Channel-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    application = factory.SubFactory(ApplicationFactory)
    project = factory.SubFactory(ProjectFactory)
    dispatcher = fqn(TestDispatcher)
    config = {"foo": "bar"}
