import logging
from typing import TYPE_CHECKING, Any

from django.db import models, transaction
from django.utils.translation import gettext as _

from .event import Event
from .validation import Validation

if TYPE_CHECKING:
    from .channel import Channel
    from .message import Message
    from .notification import Notification


logger = logging.getLogger(__name__)


class Occurrence(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    context = models.JSONField(blank=True, null=True)
    processed = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))
    status = models.JSONField(default=dict)

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
        delivered = self.status.get("delivered", [])
        recipients = self.status.get("recipients", [])
        channels = self.event.channels.active()

        for notification in self.event.notifications.all():
            context = notification.get_context(self.get_context())
            for channel in channels:
                for validation in notification.get_pending_subscriptions(delivered, channel):
                    with transaction.atomic(durable=True):
                        notification.notify_to_channel(channel, validation, context)

                        delivered.append(validation.id)
                        recipients.append([validation.address.value, validation.channel.name])
                        self.status = {"delivered": delivered, "recipients": recipients}
                        self.save()
        return True
