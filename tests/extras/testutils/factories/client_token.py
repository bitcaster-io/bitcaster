import factory

from django.utils import timezone

from bitcaster.models import ClientToken

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory
from .user import UserFactory


class ClientTokenFactory(AutoRegisterModelFactory[ClientToken]):
    class Meta:
        model = ClientToken

    organization = factory.SubFactory(OrganizationFactory)
    project = factory.SubFactory(ProjectFactory)
    application = factory.SubFactory(ApplicationFactory)
    user = factory.SubFactory(UserFactory)
    allowed_origins = ["https://example.com"]
    expires_at = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(hours=1))
