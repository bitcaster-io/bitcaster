from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import QuerySet

from .distribution import DistributionList
from .validation import Validation

if TYPE_CHECKING:
    from .channel import Channel


class Notification(models.Model):
    event = models.ForeignKey("bitcaster.Event", on_delete=models.CASCADE, related_name="notifications")
    distribution = models.ForeignKey(
        DistributionList, blank=True, null=True, on_delete=models.CASCADE, related_name="notifications"
    )

    payload_filter = models.TextField(blank=True, null=True)
    extra_context = models.JSONField(default=dict)

    def get_context(self, ctx: dict[str, str]) -> dict[str, Any]:
        return {"event": self.event, **ctx}

    def get_pending_subscriptions(self, delivered: list[str], channel: "Channel") -> QuerySet[Validation]:
        return (
            self.distribution.recipients.select_related(
                "address",
                "channel",
                "address__user",
            )
            .filter(active=True, channel=channel)
            .exclude(id__in=delivered)
        )
