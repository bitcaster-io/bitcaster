from typing import TYPE_CHECKING, Any, Dict, Optional

from django.db import models

from .channel import Channel
from .mixins import SlugMixin
from .org import Application

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from .message import Message
    from .subscription import Subscription


class Event(SlugMixin, models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="events")
    description = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    locked = models.BooleanField(default=False)
    channels = models.ManyToManyField(Channel, blank=True)

    subscriptions: "QuerySet[Subscription]"
    messages: "QuerySet[Message]"

    class Meta:
        unique_together = (
            ("name", "application"),
            ("slug", "application"),
        )

    def trigger(self, context: Dict[str, Any]) -> None:
        subscription: "Subscription"
        for subscription in self.subscriptions.all():
            subscription.notify(context)

    def get_message(self, channel: "Channel") -> "Optional[Message]":
        return self.messages.filter(models.Q(channel=channel) | models.Q(channel=None)).order_by("channel").first()
