import typing

import factory
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
