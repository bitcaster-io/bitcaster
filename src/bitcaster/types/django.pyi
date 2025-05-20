from typing import TypeVar

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model
from django.forms.utils import ErrorDict

from bitcaster.models.mixins import BitcasterBaseModel

AnyModel = TypeVar("AnyModel", bound=Model | BitcasterBaseModel, covariant=True)

type AnyUser = AbstractBaseUser | AnonymousUser
JsonType = int | str | bool | list[JsonType] | dict[str, JsonType] | ErrorDict | None
