import factory
from django.contrib.auth.models import Group, Permission

from .base import AutoRegisterModelFactory
from .contenttypes import ContentTypeFactory


class PermissionFactory(AutoRegisterModelFactory):
    content_type = factory.SubFactory(ContentTypeFactory)

    class Meta:
        model = Permission


class GroupFactory(AutoRegisterModelFactory):
    name = factory.Sequence(lambda n: "group %s" % n)

    class Meta:
        model = Group
        django_get_or_create = ("name",)

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for perm in extracted:
                self.permissions.add(perm)
