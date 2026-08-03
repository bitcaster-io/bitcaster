from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from .mixins import BitcasterBaseModel


def _status_choices() -> list[tuple[str, str]]:
    from .occurrence import Occurrence

    return Occurrence.Status.choices


class DeliverySimulation(BitcasterBaseModel):
    simulation = models.ForeignKey(
        "bitcaster.EventSimulation",
        verbose_name=_("Simulation"),
        on_delete=models.CASCADE,
        related_name="deliveries",
        help_text=_("Simulation this delivery belongs to"),
    )
    assignment = models.ForeignKey(
        "bitcaster.Assignment",
        verbose_name=_("Assignment"),
        on_delete=models.CASCADE,
        related_name="simulation_deliveries",
        help_text=_("Assignment reached by this delivery"),
    )
    notification = models.ForeignKey(
        "bitcaster.Notification",
        verbose_name=_("Notification"),
        on_delete=models.CASCADE,
        related_name="simulation_deliveries",
        help_text=_("Notification sent to the assignment"),
    )
    message_template = models.ForeignKey(
        "bitcaster.MessageTemplate",
        verbose_name=_("Message template"),
        on_delete=models.CASCADE,
        related_name="simulation_deliveries",
        blank=True,
        null=True,
        help_text=_("Message template used for the delivery, if any"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=_status_choices,
        default="NEW",
        help_text=_("Status of the delivery"),
    )
    data = models.JSONField(
        verbose_name=_("Data"),
        blank=True,
        default=dict,
        help_text=_("Information about the delivery (rendered content, errors)"),
    )

    class Meta:
        verbose_name = _("Delivery simulation")
        verbose_name_plural = _("Delivery simulations")
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=("simulation", "assignment", "notification"),
                name="delivery_simulation_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["simulation", "notification"], name="delivery_simulation_sim_notif"),
        ]

    def __str__(self) -> str:
        return f"{self.simulation} - {self.assignment}"

    def natural_key(self) -> tuple[str | None, ...]:
        return str(self.pk), *self.simulation.natural_key()

    @property
    def rendered(self) -> dict[str, Any] | None:
        return self.data.get("rendered")

    @property
    def missing_template(self) -> bool:
        return self.message_template_id is None
