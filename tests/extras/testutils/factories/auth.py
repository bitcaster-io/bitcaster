import factory
from factory import Sequence
from factory.django import DjangoModelFactory

from bitcaster.auth.constants import Grant
from bitcaster.config import Group
from bitcaster.models import Role, User
from bitcaster.models.auth import ApiKey

from .org import ApplicationFactory


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ("username",)

    username = Sequence(lambda n: "user%03d" % n)
    email = Sequence(lambda n: "user%03d@localhost" % n)
    password = "password"
    # addreaa = factory.RelatedFactory(
    #     "testutils.factories.subscription.AddressFactory",
    #     factory_related_name='user',
    # )


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Role-%03d" % n)


class GroupFactory(DjangoModelFactory):
    class Meta:
        model = Group
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Group-%03d" % n)


class ApiKeyFactory(DjangoModelFactory):
    class Meta:
        model = ApiKey
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Key-%03d" % n)
    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    grants = [Grant.EVENT_TRIGGER]
