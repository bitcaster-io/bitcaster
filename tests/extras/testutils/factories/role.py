import factory
from factory import Sequence

from bitcaster.models import Role

from .base import AutoRegisterModelFactory
from .django_auth import GroupFactory
from .org import OrganizationFactory
from .user import UserFactory


class RoleFactory(AutoRegisterModelFactory):
    class Meta:
        model = Role
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Role-%03d" % n)
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    organization = factory.SubFactory(OrganizationFactory)
