from typing import TypeVar

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.db.models import Manager, Model, QuerySet
from django.forms.utils import ErrorDict

from bitcaster.models.mixins import BitcasterBaseModel

AnyModel_co = TypeVar("AnyModel_co", bound=Model | BitcasterBaseModel, covariant=True)

type AnyUser = AbstractBaseUser | AnonymousUser

M = TypeVar("M", bound=models.Model)

QuerySetOrManager = QuerySet[M] | Manager[M]
JsonType = int | str | bool | list[JsonType] | dict[str, JsonType] | ErrorDict | None
