import factory

from bitcaster.models import Occurrence

from .base import AutoRegisterModelFactory
from .event import EventFactory


class OccurrenceFactory(AutoRegisterModelFactory):
    class Meta:
        model = Occurrence

    event = factory.SubFactory(EventFactory)
    status = Occurrence.Status.NEW
    context = {}
