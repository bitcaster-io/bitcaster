import factory

from bitcaster.webpush.models import Browser

from .address import AddressFactory
from .base import AutoRegisterModelFactory
from .channel import ChannelFactory


class BrowserFactory(AutoRegisterModelFactory):
    class Meta:
        model = Browser
        django_get_or_create = ("address", "channel", "validated")

    address = factory.SubFactory(AddressFactory)
    channel = factory.SubFactory(ChannelFactory)
    validated = True
