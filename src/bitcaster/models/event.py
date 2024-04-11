from typing import TYPE_CHECKING, Any, Dict

from django.db import models
from django.utils.text import slugify

from .org import Application

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from .subscription import Subscription


class Event(models.Model):
    name = models.CharField(max_length=255, db_collation="case_insensitive")
    slug = models.SlugField(max_length=255)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="events")
    description = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)

    subscriptions: "QuerySet[Subscription]"

    class Meta:
        unique_together = (
            ("name", "application"),
            ("slug", "application"),
        )

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(str(self.name))
        super().save(*args, **kwargs)

    def trigger(self, context: Dict[str, Any]) -> None:
        subscription: "Subscription"
        for subscription in self.subscriptions.all():
            subscription.notify(context)
