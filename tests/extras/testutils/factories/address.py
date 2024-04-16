import factory

from bitcaster.models import Address

from .base import AutoRegisterModelFactory
from .user import UserFactory


class AddressFactory(AutoRegisterModelFactory):
    class Meta:
        model = Address
        django_get_or_create = ("user", "value")

    user = factory.SubFactory(UserFactory)
    value = "test@examplec.com"
    #
    # @factory.post_generation
    # def channel(self, create, extracted, **kwargs):
    #     if not create or not extracted:
    #         # Simple build, or nothing to add, do nothing.
    #         return
    #
    #     # Add the iterable of groups using bulk addition
    #     self.validate_channel(extracted)  # noqa
