from typing import Any, cast

import factory

from bitcaster.models import Member

from .base import AutoRegisterModelFactory


class MemberFactory(AutoRegisterModelFactory[Member]):
    username = factory.Sequence(lambda n: "m%03d@example.com" % n)
    email = factory.Sequence(lambda n: "m%03d@example.com" % n)
    is_active = True
    is_staff = False
    is_superuser = False

    class Meta:
        model = Member
        django_get_or_create = ("username",)

    @classmethod
    def _create(cls, model_class: Any, *args: Any, **kwargs: Any) -> "Member":
        ret = super()._create(model_class, *args, **kwargs)
        return cast("Member", ret)
