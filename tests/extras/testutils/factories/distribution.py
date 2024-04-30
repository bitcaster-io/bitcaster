import factory

from bitcaster.models import DistributionList

from .base import AutoRegisterModelFactory
from .org import ProjectFactory


class DistributionListFactory(AutoRegisterModelFactory):
    class Meta:
        model = DistributionList
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: "DistributionList-%03d" % n)
    project = factory.SubFactory(ProjectFactory)

    @factory.post_generation
    def recipients(dist: "DistributionList", create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for va in extracted:
                dist.recipients.add(va)
