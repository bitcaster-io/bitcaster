import factory

from bitcaster.models import Subscription

from .assignment import AssignmentFactory
from .base import AutoRegisterModelFactory
from .notification import NotificationFactory

__all__ = ["SubscriptionFactory", "Subscription"]


class SubscriptionFactory(AutoRegisterModelFactory[Subscription]):
    class Meta:
        model = Subscription
        django_get_or_create = ("notification", "assignment")

    notification = factory.SubFactory(NotificationFactory)
    assignment = factory.SubFactory(AssignmentFactory)
    active = True
