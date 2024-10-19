from typing import Any, cast
from uuid import uuid4

import factory
from social_django.models import UserSocialAuth

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


class SocialAuthUserFactory(UserFactory):
    @factory.post_generation  # type: ignore[misc]
    def sso(obj, create: bool, extracted: list[User], **kwargs: Any) -> None:
        UserSocialAuth.objects.get_or_create(user=obj, provider="test", uid=uuid4())
