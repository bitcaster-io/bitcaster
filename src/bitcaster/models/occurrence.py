import logging
import uuid
from typing import TYPE_CHECKING, Any

from django.db import models, transaction
from django.utils.translation import gettext as _

from ..constants import Bitcaster
from .event import Event
from .validation import Validation

if TYPE_CHECKING:
    from .channel import Channel
    from .message import Message
    from .notification import Notification


logger = logging.getLogger(__name__)


class OccurrenceQuerySet(models.QuerySet["Occurrence"]):

    def system(self, *args: Any, **kwargs: Any) -> models.QuerySet["Occurrence"]:
        return self.filter(event__application__name=Bitcaster.APPLICATION).filter(*args, **kwargs)


class Occurrence(models.Model):
    class Status(models.TextChoices):
        NEW = "NEW", _("New")
        PROCESSED = "PROCESSED", _("Processed")
        FAILED = "FAILED", _("Failed")

    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    context = models.JSONField(blank=True, null=True)
    # processed = models.BooleanField(default=False)

    correlation_id = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    recipients = models.IntegerField(default=0, help_text=_("Total number of recipients"))

    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))
    data = models.JSONField(default=dict)
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

        # self.status = {"delivered": delivered, "recipients": recipients}
        # self.save()

        for notification in self.event.notifications.all():
            context = notification.get_context(self.get_context())
            for channel in channels:
                for validation in notification.get_pending_subscriptions(delivered, channel):
                    with transaction.atomic(durable=True):
                        notification.notify_to_channel(channel, validation, context)

                        delivered.append(validation.id)
                        recipients.append([validation.address.value, validation.channel.name])

                        self.data = {"delivered": delivered, "recipients": recipients}
                        self.save()
        return True
