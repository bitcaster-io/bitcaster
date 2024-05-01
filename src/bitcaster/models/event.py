from typing import TYPE_CHECKING, Any, Dict

from django.db import models
from django.utils.translation import gettext as _

from .channel import Channel
from .mixins import SlugMixin
from .org import Application

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from bitcaster.models import Message, Occurrence


class Event(SlugMixin, models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="events")
    description = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    locked = models.BooleanField(default=False, help_text=_("Security lock"))
    newsletter = models.BooleanField(default=False, help_text=_("Do not customise notifications per single user"))

    channels = models.ManyToManyField(Channel, blank=True)

    # subscriptions: "QuerySet[Subscription]"
    messages: "QuerySet[Message]"

    class Meta:
        unique_together = (
            ("name", "application"),
            ("slug", "application"),
        )
        ordering = ("name",)

    def __init__(self, *args: Any, **kwargs: Any):
        self._cached_messages: dict[Channel, Message] = {}
        super().__init__(*args, **kwargs)

    def trigger(self, context: Dict[str, Any]) -> "Occurrence":
        from .occurrence import Occurrence

        return Occurrence.objects.create(event=self, context=context)

    # def subscribe(self, address_id: int, channel_id: int) -> None:
    #     """Register a subscription to the event."""
    #     from .validation import Validation
    #
    #     validation, _ = Validation.objects.get_or_create(address_id=address_id, channel_id=channel_id)
    #     from .subscription import Subscription
    #
    #     Subscription.objects.get_or_create(event=self, validation=validation)
    #
    # def unsubscribe(self, user: "User", channel_ids: List[int] = None) -> None:
    #     """Deregister a subscription to the event."""
    #     from .subscription import Subscription
    #
    #     qs = Subscription.objects.filter(event=self, validation__address__user=user)
    #
    #     if channel_ids:
    #         qs = qs.filter(validation__channel_id__in=channel_ids)
    #
    #     qs.delete()
