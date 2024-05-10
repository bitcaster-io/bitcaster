import factory

from bitcaster.constants import AddressType
from bitcaster.models import Address

from .base import AutoRegisterModelFactory
from .user import UserFactory


class AddressFactory(AutoRegisterModelFactory):
    class Meta:
        model = Address
        django_get_or_create = ("user", "value")

    user = factory.SubFactory(UserFactory)
    value = factory.Sequence(lambda n: "m%03d@example.com" % n)
    name = factory.Sequence(lambda n: "Address-#%s" % n)
    type = AddressType.EMAIL
