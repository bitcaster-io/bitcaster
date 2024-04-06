import factory
from factory.django import DjangoModelFactory

from bitcaster.models import Subscription

from .auth import UserFactory
from .channel import ChannelFactory
from .event import EventTypeFactory


class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = Subscription
        django_get_or_create = ("user", "event")

    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventTypeFactory)

    @factory.post_generation
    def channels(self, create, extracted, **kwargs):
        if not extracted:
            # Simple build, or nothing to add, do nothing.
            extracted = [ChannelFactory()]

        # Add the iterable of groups using bulk addition
        self.channels.add(*extracted)
