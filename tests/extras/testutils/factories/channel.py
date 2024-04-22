import factory
from factory import Sequence
from strategy_field.utils import fqn
from testutils.dispatcher import TDispatcher

from bitcaster.models import Channel

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory


class ChannelFactory(AutoRegisterModelFactory):
    class Meta:
        model = Channel
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Channel-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    project = factory.SubFactory(ProjectFactory)
    application = factory.SubFactory(ApplicationFactory)
    dispatcher = fqn(TDispatcher)
    config = {"foo": "bar"}
