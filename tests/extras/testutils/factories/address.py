import factory
from factory.django import DjangoModelFactory

from bitcaster.models import Address

from .auth import UserFactory
from .channel import ChannelFactory


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address
        django_get_or_create = ("user", "value", "channel")

    user = factory.SubFactory(UserFactory)
    channel = factory.SubFactory(ChannelFactory)
    value = "test@examplec.com"
    validated = True