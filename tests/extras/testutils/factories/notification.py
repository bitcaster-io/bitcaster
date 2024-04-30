import factory

from bitcaster.models import Notification

from .base import AutoRegisterModelFactory
from .distribution import DistributionListFactory
from .event import EventFactory


class NotificationFactory(AutoRegisterModelFactory):
    class Meta:
        model = Notification
        django_get_or_create = ("event", "distribution")

    distribution = factory.SubFactory(DistributionListFactory)
    event = factory.SubFactory(EventFactory)
    extra_context = {"extra_field": "extra_value"}
