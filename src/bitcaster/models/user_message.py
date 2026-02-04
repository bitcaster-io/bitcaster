import logging
from datetime import datetime, timedelta
from typing import Any

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from strategy_field.utils import fqn

from ..config import settings
from ..dispatchers import UserMessageDispatcher
from .event import Event
from .mixins import BitcasterBaseModel, BitcasterBaselManager

logger = logging.getLogger(__name__)

LEVELS = zip(logging._nameToLevel.keys(), logging._nameToLevel.keys(), strict=False)


class UserMessageQuerySet(models.QuerySet["UserMessage"]):
    def _get_expiration_date(self) -> datetime | None:
        from bitcaster.models import Channel

        try:
            channel = Channel.objects.get(dispatcher=fqn(UserMessageDispatcher))
            days = channel.config.get("message_ttl", 7)
            return timezone.now() - timedelta(days=days)
        except Channel.DoesNotExist:
            return None

    def expired(self) -> "models.QuerySet[UserMessage]":
        if cutoff := self._get_expiration_date():
            return self.filter(created__lt=cutoff)
        return self.none()

    def active(self) -> "models.QuerySet[UserMessage]":
        if cutoff := self._get_expiration_date():
            return self.filter(created__gte=cutoff)
        return self.all()


class UserMessageManager(BitcasterBaselManager["UserMessage"]):
    def get_queryset(self) -> UserMessageQuerySet:
        return UserMessageQuerySet(self.model, using=self._db)

    def get_by_natural_key(self, pk: int, *args: Any) -> "UserMessage":
        return self.get(pk=pk)

    def expired(self) -> "models.QuerySet[UserMessage]":
        return self.get_queryset().expired()

    def active(self) -> "models.QuerySet[UserMessage]":
        return self.get_queryset().active()


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
