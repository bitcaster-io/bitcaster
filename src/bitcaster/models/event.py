from typing import TYPE_CHECKING, Any, Dict, Optional

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

    def trigger(self, context: Dict[str, Any], cid: Optional[Any] = None) -> "Occurrence":
        from .occurrence import Occurrence

        if cid:
            cid = str(cid)
        return Occurrence.objects.create(event=self, context=context, correlation_id=cid)
