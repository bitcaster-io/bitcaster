import factory
from factory import Sequence
from factory.django import DjangoModelFactory
from strategy_field.utils import fqn

from bitcaster.dispatchers.test import TestDispatcher
from bitcaster.models import Channel

from .org import OrganizationFactory


class ChannelFactory(DjangoModelFactory):
    class Meta:
        model = Channel
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Channel-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    dispatcher = fqn(TestDispatcher)
    config = {"foo": "bar"}
