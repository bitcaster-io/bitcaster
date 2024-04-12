import factory

from bitcaster.models import Subscription
from . import AddressFactory

from .base import AutoRegisterModelFactory
from .channel import ChannelFactory
from .event import EventFactory


class SubscriptionFactory(AutoRegisterModelFactory):
    class Meta:
        model = Subscription
        django_get_or_create = ("address", "event")

    address = factory.SubFactory(AddressFactory)
    event = factory.SubFactory(EventFactory)

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        if not extracted:
            # Simple build, or nothing to add, do nothing.
            extracted = [ChannelFactory()]

        # Add the iterable of groups using bulk addition
        self.channels.add(*extracted)
