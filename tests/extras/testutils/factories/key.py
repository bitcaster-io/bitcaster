import factory
from factory import Sequence

from bitcaster.auth.constants import Grant
from bitcaster.models.key import ApiKey

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory
from .user import UserFactory


class ApiKeyFactory(AutoRegisterModelFactory[ApiKey]):
    class Meta:
        model = ApiKey
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "Key-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    project = factory.SubFactory(ProjectFactory)
    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    grants = [Grant.EVENT_TRIGGER]
