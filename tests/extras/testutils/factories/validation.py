import factory

from bitcaster.models.address import Validation

from .address import AddressFactory
from .base import AutoRegisterModelFactory
from .channel import ChannelFactory


class ValidationFactory(AutoRegisterModelFactory):
    class Meta:
        model = Validation
        django_get_or_create = ("address", "channel", "validated")

    address = factory.SubFactory(AddressFactory)
    channel = factory.SubFactory(ChannelFactory)
    validated = True
