import logging

from django.db import models
from django.utils.translation import gettext_lazy as _

from .org import Project
from .validation import Validation

logger = logging.getLogger(__name__)


class DistributionList(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Validation)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Distribution List")
        verbose_name_plural = _("Distribution Lists")
        unique_together = (("name", "project"),)
