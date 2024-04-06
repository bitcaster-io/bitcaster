from typing import TYPE_CHECKING, Any, Dict

from django.db import models

from .org import Application

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from .subscription import Subscription


class EventType(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    active = models.BooleanField(default=True)

    subscriptions: "QuerySet[Subscription]"

    def trigger(self, context: Dict[str, Any]) -> None:
        subscription: "Subscription"
        for subscription in self.subscriptions.all():
            subscription.notify(context)
