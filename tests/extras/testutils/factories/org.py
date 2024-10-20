import factory

from bitcaster.models import Application, Organization, Project

from .base import AutoRegisterModelFactory
from .user import UserFactory

__all__ = ["OrganizationFactory", "ApplicationFactory", "ProjectFactory"]


class OrganizationFactory(AutoRegisterModelFactory[Organization]):
    name = factory.Sequence(lambda n: "Organization-%03d" % n)
    slug = factory.Sequence(lambda n: "org-%03d" % n)
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Organization
        django_get_or_create = ("name",)


class ProjectFactory(AutoRegisterModelFactory[Project]):
    name = factory.Sequence(lambda n: "Project-%03d" % n)
    slug = factory.Sequence(lambda n: "project-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    owner = factory.SubFactory(UserFactory)
    environments: list[str] = []

    class Meta:
        model = Project
        django_get_or_create = ("name", "organization")


class ApplicationFactory(AutoRegisterModelFactory[Application]):
    name = factory.Sequence(lambda n: "Application-%03d" % n)
    slug = factory.Sequence(lambda n: "app-%03d" % n)
    project = factory.SubFactory(ProjectFactory)
    from_email = factory.Faker("email")
    owner = factory.SubFactory(UserFactory)

    class Meta:
        model = Application
        django_get_or_create = ("name", "project")
