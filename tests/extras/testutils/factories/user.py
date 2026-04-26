from typing import Any, cast

import factory

from bitcaster.models import User

from .base import AutoRegisterModelFactory


class UserFactory(AutoRegisterModelFactory[User]):
    _password = "password"
    username = factory.Sequence(lambda n: "m%03d@example.com" % n)
    password = factory.django.Password(_password)
    email = factory.Sequence(lambda n: "m%03d@example.com" % n)
    is_active = True
    is_staff = True

    class Meta:
        model = User
        django_get_or_create = ("username",)

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> "User":
        ret = super()._create(model_class, *args, **kwargs)
        ret._password = cls._password
        return cast("User", ret)


class SuperUserFactory(UserFactory):
    username = factory.Sequence(lambda n: "superuser%03d@example.com" % n)
    email = factory.Sequence(lambda n: "superuser%03d@example.com" % n)
    is_superuser = True
    is_staff = True
    is_active = True
