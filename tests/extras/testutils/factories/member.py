from typing import Any, cast

import factory

from bitcaster.constants import bitcaster
from bitcaster.models import Member, UserRole

from .base import AutoRegisterModelFactory
from .org import OrganizationFactory


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
        org = kwargs.pop("organization", None)
        ret = super()._create(model_class, *args, **kwargs)
        group = bitcaster.get_default_group()
        if not org:
            org = OrganizationFactory()
        UserRole.objects.create(user=ret, organization=org, group=group)
        return cast("Member", ret)
