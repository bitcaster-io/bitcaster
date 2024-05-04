import factory

from bitcaster.models import UserRole

from .base import AutoRegisterModelFactory
from .django_auth import GroupFactory
from .org import OrganizationFactory
from .user import UserFactory


class UserRoleFactory(AutoRegisterModelFactory):
    class Meta:
        model = UserRole
        django_get_or_create = ("user", "group", "organization")

    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    organization = factory.SubFactory(OrganizationFactory)
