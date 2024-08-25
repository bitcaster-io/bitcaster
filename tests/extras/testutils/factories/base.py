import typing

import factory
from django.db.models import Model
from factory.base import FactoryMetaClass

TAutoRegisterModelFactory = typing.TypeVar("TAutoRegisterModelFactory")

factories_registry: dict[Model, TAutoRegisterModelFactory] = {}  # type: ignore
T = typing.TypeVar("T")


class AutoRegisterFactoryMetaClass(FactoryMetaClass):  # type: ignore
    def __new__(mcs, class_name: str, bases: typing.Any, attrs: typing.Any) -> typing.Any:
        new_class = super().__new__(mcs, class_name, bases, attrs)
        factories_registry[new_class._meta.model] = new_class
        return new_class


class AutoRegisterModelFactory(
    factory.django.DjangoModelFactory[T], typing.Generic[T], metaclass=AutoRegisterFactoryMetaClass  # type: ignore
):
    pass
