import logging
from typing import Any, Dict

from django.db import models
from django.db.models import UniqueConstraint
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _

from ..dispatchers.base import Capability
from .channel import Channel
from .event import Event
from .mixins import ScopedMixin
from .notification import Notification

logger = logging.getLogger(__name__)


class Message(ScopedMixin, models.Model):
    name = models.CharField(_("Name"), max_length=255)
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name="messages",
        help_text=_("Channel for which  the message is valid"),
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="messages",
        help_text=_("Event to which this message belongs"),
    )
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="messages",
        help_text=_("Notification to which this message belongs"),
    )
    subject = models.TextField(_("subject"), blank=True, null=True, help_text=_("The subject of the message"))
    content = models.TextField(_("content"), blank=True, help_text=_("The content of the message"))
    html_content = models.TextField(
        _("HTML Content"), blank=True, help_text=_("The HTML formatted content of the message")
    )

    class Meta:
        verbose_name = _("Message template")
        verbose_name_plural = _("Message templates")
        ordering = ("name",)

        constraints = [
            UniqueConstraint(
                fields=["channel", "event", "name"],
                name="unique_message",
            )
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        if self.notification:
            self.event = self.notification.event

    def support_subject(self) -> bool:
        return self.channel.dispatcher.protocol.has_capability(Capability.SUBJECT)

    def support_html(self) -> bool:
        return self.channel.dispatcher.protocol.has_capability(Capability.HTML)

    def support_text(self) -> bool:
        return self.channel.dispatcher.protocol.has_capability(Capability.TEXT)

    def render(self, context: Dict[str, Any]) -> str:
        tpl = Template(self.content)
        return tpl.render(Context(context))

    def clone(self, channel: Channel) -> "Message":
        return Message.objects.get_or_create(
            organization=self.organization,
            event=self.event,
            notification=self.notification,
            channel=channel,
            content=self.content,
            html_content=self.html_content,
            subject=self.subject,
        )[0]
