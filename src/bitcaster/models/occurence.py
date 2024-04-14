from django.db import models

from .event import Event
from .subscription import Subscription


class Occurence(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    context = models.JSONField(blank=True, null=True)
    processed = models.BooleanField(default=False)

    def process(self) -> None:
        subscription: "Subscription"
        for subscription in self.event.subscriptions.all():
            subscription.notify(self.context)
