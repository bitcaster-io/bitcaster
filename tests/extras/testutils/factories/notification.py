import factory

from bitcaster.models import Notification
from bitcaster.models.choices import FILTERING_NONE

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
    active = True
    policy = FILTERING_NONE
    extra_context = {"extra_field": "extra_value"}
    recipients_filter = {}
