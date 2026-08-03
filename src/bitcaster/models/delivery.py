from typing import Any

import logging
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .mixins import BitcasterBaseModel

logger = logging.getLogger(__name__)


class Delivery(BitcasterBaseModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", _("Pending")
        DELIVERED = "DELIVERED", _("Delivered")
        ERROR = "ERROR", _("Error")
        FAILURE = "FAILURE", _("Failure")

    occurrence = models.ForeignKey(
        "bitcaster.Occurrence",
        verbose_name=_("Occurrence"),
        on_delete=models.CASCADE,
        related_name="deliveries",
        help_text=_("Occurrence this delivery belongs to"),
    )
    assignment = models.ForeignKey(
        "bitcaster.Assignment",
        verbose_name=_("Assignment"),
        on_delete=models.CASCADE,
        related_name="deliveries",
        help_text=_("Assignment that receives the message"),
    )
    notification = models.ForeignKey(
        "bitcaster.Notification",
        verbose_name=_("Notification"),
        on_delete=models.CASCADE,
        related_name="deliveries",
        help_text=_("Notification sent to the assignment"),
    )
    channel = models.ForeignKey(
        "bitcaster.Channel",
        verbose_name=_("Channel"),
        on_delete=models.CASCADE,
        related_name="deliveries",
        help_text=_("Channel used to send the message"),
    )
    message_template = models.ForeignKey(
        "bitcaster.MessageTemplate",
        verbose_name=_("Message template"),
        on_delete=models.CASCADE,
        related_name="deliveries",
        blank=True,
        null=True,
        help_text=_("Message template used for the delivery, if any"),
    )
    status = models.CharField(
        verbose_name=_("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_("Status of the delivery"),
    )
    errors = models.IntegerField(
        verbose_name=_("Errors"),
        default=0,
        help_text=_("Number of sending errors"),
    )
    next_attempt_at = models.DateTimeField(
        verbose_name=_("Next attempt"),
        blank=True,
        null=True,
        help_text=_("Timestamp of the next allowed sending attempt. Null means due immediately"),
    )
    data = models.JSONField(
        verbose_name=_("Data"),
        blank=True,
        default=dict,
        help_text=_("Information about the delivery (rendered content, errors)"),
    )

    class Meta:
        verbose_name = _("Delivery")
        verbose_name_plural = _("Deliveries")
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=("occurrence", "assignment", "notification", "channel"),
                name="delivery_unique",
            ),
        ]
        indexes = [
            models.Index(fields=["status", "next_attempt_at"], name="delivery_status_next_attempt"),
        ]

    def __str__(self) -> str:
        return f"{self.occurrence} - {self.assignment}"

    def natural_key(self) -> tuple[str | None, ...]:
        return str(self.pk), *self.occurrence.natural_key()

    @property
    def rendered(self) -> dict[str, Any] | None:
        return self.data.get("rendered")

    @property
    def missing_template(self) -> bool:
        return self.message_template_id is None

    def mark_error(self) -> None:
        from constance import config

        self.errors = self.errors + 1
        if self.errors >= config.MAX_DELIVERY_RETRIES:
            self.status = self.Status.FAILURE
            self.next_attempt_at = None
        else:
            self.status = self.Status.ERROR
            self.next_attempt_at = timezone.now() + timedelta(minutes=config.DELIVERY_RETRY_DELAY)
        self.save(update_fields=["errors", "status", "next_attempt_at", "last_updated"])

    def send(self) -> bool:
        from bitcaster.dispatchers.base import Payload

        rendered = self.rendered or {}
        payload = Payload(
            event=self.occurrence.event,
            user=self.assignment.address.user,
            subject=rendered.get("subject", ""),
            message=rendered.get("message", ""),
            html_message=rendered.get("html_message", ""),
        )
        self.channel.dispatcher.send(self.assignment.address.value, payload, assignment=self.assignment)
        self.status = self.Status.DELIVERED
        self.save(update_fields=["status", "last_updated"])
        return True
