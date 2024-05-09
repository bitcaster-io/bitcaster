import factory
from django.core.files.base import ContentFile
from factory import Sequence

from bitcaster.models import MediaFile

from .base import AutoRegisterModelFactory
from .org import ApplicationFactory, OrganizationFactory, ProjectFactory


class MediaFileFactory(AutoRegisterModelFactory):
    class Meta:
        model = MediaFile
        django_get_or_create = ("name",)

    name = Sequence(lambda n: "file-%03d" % n)
    organization = factory.SubFactory(OrganizationFactory)
    project = factory.SubFactory(ProjectFactory)
    application = factory.SubFactory(ApplicationFactory)
    image = factory.LazyAttribute(
        lambda _: ContentFile(factory.django.ImageField()._make_data({"width": 1024, "height": 768}), "logo.png")
    )

    @classmethod
    def create(cls, **kwargs):
        if kwargs.get("application", None):
            kwargs["project"] = kwargs["application"].project
        if kwargs.get("project", None):
            kwargs["organization"] = kwargs["project"].organization
        if not kwargs.get("organization", None):
            kwargs["organization"] = OrganizationFactory()

        return super().create(**kwargs)
