from typing import TYPE_CHECKING, Any

import logging
from datetime import timedelta

from constance import config

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .event import Event
from .mixins import BitcasterBaseModel, BitcasterBaselManager

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from .occurrence import OccurrenceData

logger = logging.getLogger(__name__)


def _status_choices() -> list[tuple[str, str]]:
    from .occurrence import Occurrence

    return Occurrence.Status.choices


class EventSimulationManager(BitcasterBaselManager["EventSimulation"]):
    def purgeable(self, *args: Any, **kwargs: Any) -> "QuerySet[EventSimulation]":
        return self.filter(timestamp__lt=timezone.now() - timedelta(days=config.EVENT_SIMULATION_RETENTION)).filter(
            *args, **kwargs
        )


class EventSimulation(BitcasterBaseModel):
    class Mode(models.TextChoices):
        FAST = "fast", _("Fast")
        FULL = "full", _("Full")
        PARTIAL = "partial", _("Partial")

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="simulations")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    context = models.JSONField(
        verbose_name=_("Context"), blank=True, default=dict, help_text=_("Sample context used for the simulation")
    )
    options = models.JSONField(
        verbose_name=_("Options"),
        blank=True,
        default=dict,
        help_text=_("Options provided by the sender to route linked notifications"),
    )
    mode = models.CharField(
        verbose_name=_("Mode"),
        max_length=20,
        choices=Mode.choices,
        help_text=_("Depth of the simulation"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=_status_choices,
        default="NEW",
        help_text=_("Status of the simulation"),
    )
    data = models.JSONField(
        verbose_name=_("Data"),
        blank=True,
        default=dict,
        help_text=_("Information about the processing (recipients, channels)"),
    )
    timestamp = models.DateTimeField(
        verbose_name=_("Date"), auto_now_add=True, help_text=_("Timestamp when simulation has been created.")
    )

    objects = EventSimulationManager()

    class Meta:
        verbose_name = _("Event simulation")
        verbose_name_plural = _("Event simulations")
        ordering = ("-timestamp",)

    def __str__(self) -> str:
        return f"{self.event.name} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def natural_key(self) -> tuple[str | None, ...]:
        return str(self.pk), *self.event.natural_key()

    def save_deliveries(self, data: "OccurrenceData") -> None:
        """Persist the per-recipient preview transcript into `DeliverySimulation` rows.

        Consumes the `OccurrenceData` returned by `Occurrence.preview`, stores one
        `DeliverySimulation` row per (assignment, notification) and trims `self.data`
        down to the aggregate summary. The row writing and the state transition to
        PROCESSED are atomic and guarded by the current status so a concurrent
        completion is never overwritten.
        """
        from .deliverysimulation import DeliverySimulation
        from .occurrence import Occurrence

        deliveries = self._collect_deliveries(data)
        summary = self._delivery_summary(data)
        with transaction.atomic():
            updated = bool(
                type(self)
                .objects.filter(pk=self.pk, status=Occurrence.Status.NEW)
                .update(data=summary, status=Occurrence.Status.PROCESSED)
            )
            if updated:
                self.deliveries.all().delete()
                DeliverySimulation.objects.bulk_create(deliveries, batch_size=1000)

    def _collect_deliveries(self, data: "OccurrenceData") -> "list[Any]":
        from .deliverysimulation import DeliverySimulation
        from .occurrence import Occurrence

        recipients: list[Any] = data.get("recipients", [])
        rendered = {f"{r['assignment_pk']}-{r['notification_pk']}": r for r in data.get("rendered", [])}
        assignment_pks = {e[2] for e in recipients}
        notification_pks = {e[4] for e in recipients if e[4] is not None}
        template_pks = {e[5] for e in recipients if e[5] is not None}
        assignments = self._in_bulk("Assignment", assignment_pks)
        notifications = self._in_bulk("Notification", notification_pks)
        templates = self._in_bulk("MessageTemplate", template_pks)
        deliveries: list[Any] = []
        for _addr, _channel_name, assignment_pk, _channel_pk, notification_pk, template_pk in recipients:
            entry = rendered.get(f"{assignment_pk}-{notification_pk}")
            row: dict[str, Any] = {}
            if entry:
                row["rendered"] = {
                    "subject": entry["subject"],
                    "message": entry["message"],
                    "html_message": entry["html_message"],
                }
            deliveries.append(
                DeliverySimulation(
                    simulation=self,
                    assignment=assignments[assignment_pk],
                    notification=notifications[notification_pk],
                    message_template=templates.get(template_pk),
                    status=Occurrence.Status.PROCESSED,
                    data=row,
                )
            )
        return deliveries

    @staticmethod
    def _in_bulk(model_name: str, pks: set[int]) -> dict[int, Any]:
        from django.apps import apps

        if not pks:
            return {}
        model = apps.get_model("bitcaster", model_name)
        return model.objects.in_bulk(pks)

    @staticmethod
    def _delivery_summary(data: "OccurrenceData") -> dict[str, Any]:
        return {
            "delivered": data.get("delivered", []),
            "errors": data.get("errors", []),
            "notifications": data.get("notifications", []),
            "channels": data.get("channels", []),
            "messages": data.get("messages", []),
            "recipients_count": len(data.get("recipients", [])),
            "rendered_count": len(data.get("rendered", [])),
            "missing_template_count": len(data.get("missing_template", [])),
        }
