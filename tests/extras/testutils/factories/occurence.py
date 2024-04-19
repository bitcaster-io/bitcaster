import factory

from bitcaster.models import Occurrence

from .base import AutoRegisterModelFactory
from .event import EventFactory


class OccurenceFactory(AutoRegisterModelFactory):
    class Meta:
        model = Occurrence

    event = factory.SubFactory(EventFactory)
    processed = False
    context = {}
