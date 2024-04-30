import factory
from factory import Sequence

from bitcaster.models import Event

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory


class EventFactory(AutoRegisterModelFactory):
    class Meta:
        model = Event
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Event-%03d" % n)
    application = factory.SubFactory(ApplicationFactory)

    @factory.post_generation
    def channels(dist: "Event", create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for ch in extracted:
                dist.channels.add(ch)
