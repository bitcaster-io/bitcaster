import logging
from typing import TYPE_CHECKING, Any, Optional

from django.db import models, transaction
from django.utils.translation import gettext as _

from ..dispatchers.base import Dispatcher, Payload
from . import Address
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

    # def get_pending_subscriptions(self):
    #     delivered = self.status.get("delivered", [])
    #     return (
    #         self.event.subscriptions.select_related(
    #             "validation__address",
    #             "validation__channel",
    #         )
    #         .filter(active=True)
    #         .exclude(id__in=delivered)
    #     )
    def notify_to_channel(self, channel: "Channel", validation: Validation, context: dict[str, Any]) -> str:
        message: Optional["Message"]

        dispatcher: "Dispatcher" = channel.dispatcher
        addr: "Address" = validation.address
        if message := self.event.get_message(channel):
            context.update({"channel": channel, "address": addr.value})
            payload: Payload = Payload(
                event=self.event,
                user=addr.user,
                message=message.render(context),
            )
            dispatcher.send(addr.value, payload)
        return addr.value

    def process(self) -> None:
        validation: "Validation"
        notification: "Notification"
        delivered = self.status.get("delivered", [])
        recipients = self.status.get("recipients", [])
        channels = self.event.channels.active()
        for notification in self.event.notifications.all():
            context = notification.get_context(self.context)
            for channel in channels:
                for validation in notification.get_pending_subscriptions(delivered, channel):
                    with transaction.atomic(durable=True):
                        self.notify_to_channel(channel, validation, context)
                        delivered.append(validation.id)
                        recipients.append([validation.address.value, validation.channel.name])
                        self.status = {"delivered": delivered, "recipients": recipients}
                        self.save()
