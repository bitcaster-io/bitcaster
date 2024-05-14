import logging
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .assignment import Assignment
from .mixins import BitcasterBaselManager, BitcasterBaseModel
from .project import Project

logger = logging.getLogger(__name__)


class DistributionListManager(BitcasterBaselManager["DistributionList"]):

    def get_by_natural_key(self, name: "str", prj: "str", org: str, *args: Any) -> "DistributionList":
        return self.get(project__organization__slug=org, project__slug=prj, name=name)


class DistributionList(BitcasterBaseModel):
    ADMINS = "Bitcaster Admins"
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Assignment)

    objects = DistributionListManager()

    def __str__(self) -> str:
        return self.name

    def natural_key(self) -> tuple[str | None, ...]:
        return self.name, *self.project.natural_key()

    class Meta:
        verbose_name = _("Distribution List")
        verbose_name_plural = _("Distribution Lists")
        unique_together = (("name", "project"),)
