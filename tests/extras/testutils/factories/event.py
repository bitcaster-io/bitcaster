import factory
from factory import Sequence
from factory.django import DjangoModelFactory

from bitcaster.models import Application, Organization, Project, EventType, Channel
from testutils.factories import ApplicationFactory, OrganizationFactory


class ChannelFactory(DjangoModelFactory):
    class Meta:
        model = Channel
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Event-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    dispatcher = "test"

class EventTypeFactory(DjangoModelFactory):
    class Meta:
        model = EventType
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Event-%03d" % n)
    application = factory.SubFactory(ApplicationFactory)
