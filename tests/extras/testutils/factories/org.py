import factory
from factory import Sequence

from bitcaster.models import Application, Organization, Project

from .base import AutoRegisterModelFactory
from .user import UserFactory


class OrganizationFactory(AutoRegisterModelFactory):
    class Meta:
        model = Organization
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Organization-%03d" % n)
    owner = factory.SubFactory(UserFactory)


class ProjectFactory(AutoRegisterModelFactory):
    class Meta:
        model = Project
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Project-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    owner = factory.SubFactory(UserFactory)


class ApplicationFactory(AutoRegisterModelFactory):
    class Meta:
        model = Application
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Application-%03d" % n)
    project = factory.SubFactory(ProjectFactory)
    from_email = factory.Faker("email")
    owner = factory.SubFactory(UserFactory)
