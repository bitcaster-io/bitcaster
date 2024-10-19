import factory

from bitcaster.models import Notification

from .base import AutoRegisterModelFactory
from .distribution import DistributionListFactory
from .event import EventFactory

__all__ = ["NotificationFactory", "Notification"]


class NotificationFactory(AutoRegisterModelFactory[Notification]):
    class Meta:
        model = Notification
        django_get_or_create = ("event", "distribution")

    name = factory.Sequence(lambda n: f"Notification {n}")
    distribution = factory.SubFactory(DistributionListFactory)
    event = factory.SubFactory(EventFactory)
    extra_context = {"extra_field": "extra_value"}
