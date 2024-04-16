import factory

from bitcaster.models import Subscription
from .base import AutoRegisterModelFactory
from .channel import ChannelFactory


class SubscriptionFactory(AutoRegisterModelFactory):
    from .event import EventFactory
    from .validation import ValidationFactory

    class Meta:
        model = Subscription
        django_get_or_create = ("validation", "event")

    validation = factory.SubFactory(ValidationFactory)
    event = factory.SubFactory(EventFactory)

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        if not extracted:
            # Simple build, or nothing to add, do nothing.

            extracted = [ChannelFactory()]

        # Add the iterable of groups using bulk addition
        self.channels.add(*extracted)
