import logging
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _

from ..dispatchers.base import Capability
from .channel import Channel
from .event import Event
from .mixins import BitcasterBaseModel, BitcasterBaselManager, Scoped3Mixin
from .notification import Notification

if TYPE_CHECKING:
    from bitcaster.models import Application


logger = logging.getLogger(__name__)


class MessageManager(BitcasterBaselManager["Message"]):
    def get_by_natural_key(self, name: str, app: str, prj: str, org: str) -> "Message":
        filters: dict[str, str | None] = {}
        if app:
            filters["application__slug"] = app
        else:
            filters["application"] = None

        if prj:
            filters["project__slug"] = prj
        else:
            filters["project"] = None

        return self.get(name=name, organization__slug=org, **filters)


class Message(Scoped3Mixin, BitcasterBaseModel):
    application: "Application"

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
    objects = MessageManager()

    class Meta:
        verbose_name = _("Message template")
        verbose_name_plural = _("Message templates")
        ordering = ("name",)

        constraints = [
            UniqueConstraint(fields=["notification", "channel"], name="unique_message_for_notification"),
            UniqueConstraint(fields=["organization", "project", "name"], name="unique_message_prj"),
            UniqueConstraint(fields=["organization", "project", "application", "name"], name="unique_message_app"),
            UniqueConstraint(fields=["organization", "name"], name="unique_message_org"),
        ]

    def __str__(self) -> str:
        return self.name

    def natural_key(self) -> tuple[str, str, str, str] | tuple[str, None, str, str] | tuple[str, None, None, str]:
        if self.application:
            return self.name, *self.application.natural_key()
        if self.project:
            return self.name, None, *self.project.natural_key()
        return self.name, None, None, *self.organization.natural_key()

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

    #
    # def render(self, context: Dict[str, Any]) -> str:
    #     tpl = Template(self.content)
    #     return tpl.render(Context(context))

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
