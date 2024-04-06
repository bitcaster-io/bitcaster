import factory
from factory import Sequence
from factory.django import DjangoModelFactory
from bitcaster.models import EventType

from .org import ApplicationFactory


class EventTypeFactory(DjangoModelFactory):
    class Meta:
        model = EventType
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Event-%03d" % n)
    application = factory.SubFactory(ApplicationFactory)
