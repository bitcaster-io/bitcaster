import logging
from typing import TYPE_CHECKING, Any, Dict

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..dispatchers.base import Dispatcher, Payload
from .auth import User
from .channel import Channel
from .event import EventType

if TYPE_CHECKING:
    from .message import Message

logger = logging.getLogger(__name__)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriptions")
    event = models.ForeignKey(EventType, on_delete=models.CASCADE, related_name="subscriptions")
    channels = models.ManyToManyField(Channel, related_name="subscriptions")

    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")

    def notify(self, context: Dict[str, Any]) -> None:
        message: "Message"
        context.update({"subscription": self, "event": self.event})
        for ch in self.channels.active():
            dispatcher: "Dispatcher" = ch.dispatcher            
            if addr := self.user.addresses.filter(validated=True, channel=ch).first():
                if message := self.event.messages.filter(channel=ch).first():
                    context.update({"channel": ch, "address": addr})
                    payload: Payload = Payload(
                        user=self.user,
                        message=message.render(context),
                    )
                    dispatcher.send(addr.value, payload)
