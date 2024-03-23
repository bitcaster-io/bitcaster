import typing

import factory
from factory import Faker
from factory.base import FactoryMetaClass

TAutoRegisterModelFactory = typing.TypeVar("TAutoRegisterModelFactory", bound="AutoRegisterModelFactory")

factories_registry: dict[str, TAutoRegisterModelFactory] = {}


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name, bases, attrs):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class AutoRegisterModelFactory(factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass):
    pass


class HopeAutoRegisterModelFactory(AutoRegisterModelFactory):
    id = Faker("uuid4")
    # id = factory.LazyFunction(lambda: str(uuid.uuid4()))

    # @classmethod
    # def create(cls, **kwargs):
    #     if "id" in kwargs:
    #         uuid.UUID(kwargs['id'])
    #     else:
    #         kwargs['id'] = str(uuid.uuid4())
    #
    #     return super().create(**kwargs)
    #
    # @classmethod
    # def _adjust_kwargs(cls, **kwargs):
    #     # Ensure ``lastname`` is upper-case.
    #     # try:
    #     uuid.UUID(kwargs['id'])
    #     # except:
    #     #     kwargs['id'] = str(uuid.uuid4())
    #
    #     return kwargs
