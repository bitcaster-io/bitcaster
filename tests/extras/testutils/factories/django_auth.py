from typing import Any

import factory
from django.contrib.auth.models import Group, Permission

from .base import AutoRegisterModelFactory
from .contenttypes import ContentTypeFactory


class PermissionFactory(AutoRegisterModelFactory[Permission]):
    content_type = factory.SubFactory(ContentTypeFactory)

    class Meta:
        model = Permission


class GroupFactory(AutoRegisterModelFactory[Group]):
    name = factory.Sequence(lambda n: "group %s" % n)

    class Meta:
        model = Group
        django_get_or_create = ("name",)

    @factory.post_generation  # type: ignore[misc]
    def permissions(self, create: bool, extracted: list[str], **kwargs: Any) -> None:
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for perm in extracted:
                self.permissions.add(perm)
