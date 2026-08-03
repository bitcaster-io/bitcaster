import factory

from bitcaster.models import DeliverySimulation, Occurrence

from .assignment import AssignmentFactory
from .base import AutoRegisterModelFactory
from .eventsimulation import EventSimulationFactory
from .notification import NotificationFactory


class DeliverySimulationFactory(AutoRegisterModelFactory[DeliverySimulation]):
    class Meta:
        model = DeliverySimulation

    simulation = factory.SubFactory(EventSimulationFactory)
    assignment = factory.SubFactory(AssignmentFactory)
    notification = factory.SubFactory(NotificationFactory)
    status = Occurrence.Status.NEW
    data: dict[str, object] = {}
