import logging
from typing import Any

from django.db import models
from django.utils.translation import gettext_lazy as _

from ..config import settings
from .event import Event
from .mixins import BitcasterBaseModel, BitcasterBaselManager

logger = logging.getLogger(__name__)

LEVELS = zip(logging._nameToLevel.keys(), logging._nameToLevel.keys(), strict=False)


class UserMessageManager(BitcasterBaselManager["UserMessage"]):
    def get_by_natural_key(self, pk: int, *args: Any) -> "UserMessage":
        return self.get(pk=pk)


class UserMessage(BitcasterBaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bitcaster_messages")
    level = models.CharField(max_length=255, choices=LEVELS, default=logging.INFO)
    subject = models.TextField()
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)

    read = models.DateTimeField(blank=True, null=True, default=None)
    displayed = models.BooleanField(blank=True, null=True, default=None)

    objects = UserMessageManager()

    class Meta:
        verbose_name = _("User Message")
        verbose_name_plural = _("User Messages")
        app_label = "bitcaster"

    def natural_key(self) -> tuple[str]:
        return (str(self.pk),)
