from typing import TYPE_CHECKING, Any

import factory

from bitcaster.models import DistributionList

from .base import AutoRegisterModelFactory
from .org import ProjectFactory

if TYPE_CHECKING:
    from bitcaster.models import Assignment


class DistributionListFactory(AutoRegisterModelFactory[DistributionList]):
    class Meta:
        model = DistributionList
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: "DistributionList-%03d" % n)
    project = factory.SubFactory(ProjectFactory)

    @factory.post_generation  # type: ignore[misc]
    def recipients(dist: "DistributionList", create: bool, extracted: "list[Assignment]", **kwargs: Any) -> None:
        if not create:
            return

        if extracted:
            for va in extracted:
                dist.recipients.add(va)
