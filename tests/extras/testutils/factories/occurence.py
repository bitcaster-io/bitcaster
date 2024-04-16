import factory

from bitcaster.models import Occurence

from .base import AutoRegisterModelFactory
from .event import EventFactory


class OccurenceFactory(AutoRegisterModelFactory):
    class Meta:
        model = Occurence

    event = factory.SubFactory(EventFactory)
    processed = False
    context = {}
