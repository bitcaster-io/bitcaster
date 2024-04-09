import factory
from factory.django import DjangoModelFactory

from bitcaster.models.address import Validation

from .address import AddressFactory
from .channel import ChannelFactory


class ValidationFactory(DjangoModelFactory):
    class Meta:
        model = Validation
        django_get_or_create = ("address", "channel", "validated")

    address = factory.SubFactory(AddressFactory)
    channel = factory.SubFactory(ChannelFactory)
    validated = True
