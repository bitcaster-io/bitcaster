import factory

from bitcaster.models import Subscription

from .base import AutoRegisterModelFactory
from .event import EventFactory
from .validation import ValidationFactory


class SubscriptionFactory(AutoRegisterModelFactory):
    class Meta:
        model = Subscription
        django_get_or_create = ("validation", "event")

    validation = factory.SubFactory(ValidationFactory)
    event = factory.SubFactory(EventFactory)
