from typing import TypeAlias, TypeVar

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.db.models import Model

AnyModel = TypeVar("AnyModel", bound=Model, covariant=True)
# _ModelT = TypeVar("_ModelT", bound=Model)

AnyUser: TypeAlias = AbstractBaseUser | AnonymousUser
