import factory

from bitcaster.models import Validation
from testutils.factories.address import AddressFactory
from testutils.factories.base import AutoRegisterModelFactory
from testutils.factories.channel import ChannelFactory


class ValidationFactory(AutoRegisterModelFactory):

    class Meta:
        model = Validation
        django_get_or_create = ("address", "channel", "validated")

    address = factory.SubFactory(AddressFactory)
    channel = factory.SubFactory(ChannelFactory)
    validated = True
