import factory

from bitcaster.models import EventSimulation, Occurrence

from .base import AutoRegisterModelFactory
from .event import EventFactory
from .user import UserFactory


class EventSimulationFactory(AutoRegisterModelFactory[EventSimulation]):
    class Meta:
        model = EventSimulation

    event = factory.SubFactory(EventFactory)
    created_by = factory.SubFactory(UserFactory)
    context: dict[str, object] = {}
    options: dict[str, object] = {}
    mode = EventSimulation.Mode.FAST
    status = Occurrence.Status.NEW
