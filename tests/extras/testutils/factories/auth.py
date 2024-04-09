import factory
from factory import Sequence

from bitcaster.auth.constants import Grant
from bitcaster.models import Role
from bitcaster.models.auth import ApiKey

from .base import AutoRegisterModelFactory
from .django_auth import GroupFactory
from .org import ApplicationFactory, OrganizationFactory
from .user import UserFactory

#
# class UserFactory(DjangoModelFactory):
#     class Meta:
#         model = User
#         django_get_or_create = ("username",)
#
#     username = Sequence(lambda n: "user%03d" % n)
#     email = Sequence(lambda n: "user%03d@localhost" % n)
#     password = "password"
#     # addreaa = factory.RelatedFactory(
#     #     "testutils.factories.subscription.AddressFactory",
#     #     factory_related_name='user',
#     # )


class RoleFactory(AutoRegisterModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Role-%03d" % n)
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    organization = factory.SubFactory(OrganizationFactory)


class ApiKeyFactory(AutoRegisterModelFactory):
    class Meta:
        model = ApiKey
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Key-%03d" % n)
    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    grants = [Grant.EVENT_TRIGGER]
