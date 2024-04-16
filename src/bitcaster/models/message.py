import logging
from typing import Any, Dict, Iterable, Optional

from django.db import models
from django.db.models import UniqueConstraint
from django.template import Context, Template
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from ..utils.strings import grouper
from .channel import Channel
from .event import Event

logger = logging.getLogger(__name__)


class Message(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    code = models.CharField(_("Code"), max_length=255, unique=True, blank=True)
    channel = models.ForeignKey(Channel, null=True, blank=True, on_delete=models.CASCADE, related_name="messages")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="messages")

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

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if not self.code:
            self.code = f"{slugify(self.name)}-{grouper(get_random_string(20), 4, '')}"
        super().save(force_insert, force_update, using, update_fields)

    def support_subject(self) -> bool:
        return self.channel is None or self.channel.dispatcher.has_subject

    def support_html(self) -> bool:
        return self.channel is None or self.channel.dispatcher.html_message

    def render(self, context: Dict[str, Any]) -> str:
        tpl = Template(self.content)
        return tpl.render(Context(context))

    def clone(self, channel: Channel) -> "Message":
        code = f"{slugify(self.name)}-{grouper(get_random_string(10), 4, '')}"
        return Message.objects.get_or_create(
            event=self.event,
            channel=channel,
            code=code,
            content=self.content,
            html_content=self.html_content,
            subject=self.subject,
        )[0]
