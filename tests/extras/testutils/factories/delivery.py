import factory

from bitcaster.models import Delivery

from .assignment import AssignmentFactory
from .base import AutoRegisterModelFactory
from .channel import ChannelFactory
from .notification import NotificationFactory
from .occurrence import OccurrenceFactory


class DeliveryFactory(AutoRegisterModelFactory[Delivery]):
    class Meta:
        model = Delivery

    occurrence = factory.SubFactory(OccurrenceFactory)
    assignment = factory.SubFactory(AssignmentFactory)
    notification = factory.SubFactory(NotificationFactory)
    channel = factory.SubFactory(ChannelFactory)
    status = Delivery.Status.PENDING
    data: dict[str, object] = {}
