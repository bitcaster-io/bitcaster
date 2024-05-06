import logging
import uuid
from typing import TYPE_CHECKING, Any, TypedDict

from django.db import models, transaction
from django.utils.translation import gettext as _

from ..constants import Bitcaster
from .event import Event
from .validation import Validation

if TYPE_CHECKING:
    from .channel import Channel
    from .message import Message
    from .notification import Notification

    OccurrenceData = TypedDict(
        "OccurrenceData",
        {
            "delivered": list[str | int],
            "recipients": list[tuple[str, str]],
        },
    )

    OccurrenceOptions = TypedDict(
        "OccurrenceOptions",
        {
            "limit_to": list[str],
        },
    )
logger = logging.getLogger(__name__)


class OccurrenceQuerySet(models.QuerySet["Occurrence"]):

    def system(self, *args: Any, **kwargs: Any) -> models.QuerySet["Occurrence"]:
        return self.filter(event__application__name=Bitcaster.APPLICATION).filter(*args, **kwargs)


class Occurrence(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", _("New")
        PROCESSED = "PROCESSED", _("Processed")
        FAILED = "FAILED", _("Failed")

    timestamp = models.DateTimeField(auto_now_add=True, help_text=_("Timestamp when occurrence has been created."))
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    context = models.JSONField(blank=True, default=dict, help_text=_("Context provided by the sender"))
    options: "OccurrenceOptions" = models.JSONField(  # type: ignore[assignment]
        blank=True, default=dict, help_text=_("Options provided by the sender to route linked notifications")
    )

    correlation_id = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    recipients = models.IntegerField(default=0, help_text=_("Total number of recipients"))

    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))
    data: "OccurrenceData" = models.JSONField(  # type: ignore[assignment]
        default=dict, help_text=_("Information about the processing (recipients, channels)")
    )
    status = models.CharField(
        choices=Status,
        default=Status.NEW.value,
    )

    attempts = models.IntegerField(default=5)
    objects = OccurrenceQuerySet.as_manager()

    class Meta:
        ordering = ("timestamp",)

    def __str__(self) -> str:
        return f"Occurrence of {self.event.name} on {self.timestamp}"

    def __init__(self, *args: Any, **kwargs: Any):
        self._cached_messages: dict[Channel, Message] = {}
        super().__init__(*args, **kwargs)

    def get_context(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event": self.event,
        }

    def process(self) -> bool:
        validation: "Validation"
        notification: "Notification"
        delivered = self.data.get("delivered", [])
        recipients = self.data.get("recipients", [])
        channels = self.event.channels.active()
        extra_filter = {}
        if limit := self.options.get("limit_to", []):
            extra_filter = {"address__value__in": limit}
        for notification in self.event.notifications.match(self.context):
            context = notification.get_context(self.get_context())
            for channel in channels:
                for validation in notification.get_pending_subscriptions(delivered, channel).filter(**extra_filter):
                    with transaction.atomic(durable=True):
                        notification.notify_to_channel(channel, validation, context)

                        delivered.append(validation.id)
                        recipients.append((validation.address.value, validation.channel.name))

                        self.data = {"delivered": delivered, "recipients": recipients}
                        self.save()
        return True
