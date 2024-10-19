import factory

from bitcaster.models import Assignment

from .address import AddressFactory
from .base import AutoRegisterModelFactory
from .channel import ChannelFactory


class AssignmentFactory(AutoRegisterModelFactory["Assignment"]):
    class Meta:
        model = Assignment
        django_get_or_create = ("address", "channel", "validated")

    address = factory.SubFactory(AddressFactory)
    channel = factory.SubFactory(ChannelFactory)
    validated = True
