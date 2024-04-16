from django.db import models
from django.utils.translation import gettext as _

from .event import Event
from .subscription import Subscription


class Occurence(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    context = models.JSONField(blank=True, null=True)
    processed = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))

    class Meta:
        ordering = ("timestamp",)

    def process(self) -> None:
        subscription: "Subscription"
        for subscription in self.event.subscriptions.all():
            subscription.notify(self.context)
