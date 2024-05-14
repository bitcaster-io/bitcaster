from typing import Any

from django.db import models
from django.utils.translation import gettext as _

from .mixins import BitcasterBaselManager, BitcasterBaseModel


class AssignmentManager(BitcasterBaselManager["Assignment"]):

    def get_by_natural_key(self, user: str, addr: str, ch: str, app: str, prj: str, org: str) -> "Assignment":
        filters: dict[str, Any] = {}
        if app:
            filters["channel__application__slug"] = app
        else:
            filters["channel__application"] = None

        if prj:
            filters["channel__project__slug"] = prj
        else:
            filters["channel__project"] = None
        return self.get(
            address__user__username=user,
            address__name=addr,
            channel__organization__slug=org,
            channel__name=ch,
            **filters,
        )


class Assignment(BitcasterBaseModel):
    address = models.ForeignKey("bitcaster.Address", on_delete=models.CASCADE, related_name="assignments")
    channel = models.ForeignKey("bitcaster.Channel", on_delete=models.CASCADE, related_name="assignments")
    validated = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    data = models.JSONField(default=dict, blank=True, null=True)

    objects = AssignmentManager()

    class Meta:
        verbose_name = _("Assignment")
        verbose_name_plural = _("Assignments")
        unique_together = (("address", "channel"),)

    def natural_key(self) -> tuple[str | None, ...]:
        return *self.address.natural_key(), *self.channel.natural_key()

    def __str__(self) -> str:
        return f"{self.address} - {self.channel}"
