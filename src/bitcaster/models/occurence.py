import logging

from django.db import models, transaction
from django.utils.translation import gettext as _

from .event import Event
from .subscription import Subscription

logger = logging.getLogger(__name__)


class Occurence(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    context = models.JSONField(blank=True, null=True)
    processed = models.BooleanField(default=False)
    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))
    status = models.JSONField(blank=True, null=True, default=dict)

    class Meta:
        ordering = ("timestamp",)

    def process(self) -> None:
        subscription: "Subscription"
        delivered = self.status.get("delivered", [])
        recipients = self.status.get("recipients", [])
        for subscription in self.event.subscriptions.select_related(
            "validation__address",
            "validation__channel",
        ).exclude(active=True, id__in=delivered):
            with transaction.atomic(durable=True):
                subscription.notify(dict(self.context))
                delivered.append(subscription.id)
                recipients.append([subscription.validation.address.value, subscription.validation.channel.name])
                self.status = {"delivered": delivered, "recipients": recipients}
                self.save()
