import typing

import factory
from django.db.models import Model
from factory.base import FactoryMetaClass

TAutoRegisterModelFactory = typing.TypeVar("TAutoRegisterModelFactory", bound="AutoRegisterModelFactory")

factories_registry: dict[Model, TAutoRegisterModelFactory] = {}
T = typing.TypeVar("T")


class AutoRegisterFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, class_name: str, bases: typing.Any, attrs: typing.Any):
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class AutoRegisterModelFactory(
    typing.Generic[T], factory.django.DjangoModelFactory, metaclass=AutoRegisterFactoryMetaClass
):
    pass
