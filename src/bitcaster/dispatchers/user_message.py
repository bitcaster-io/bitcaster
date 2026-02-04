import logging
from typing import TYPE_CHECKING, Any

from constance import config
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from unfold.widgets import UnfoldAdminSelect2Widget

from ..utils.shortcuts import render_string
from .base import Dispatcher, DispatcherConfig, MessageProtocol, Payload

if TYPE_CHECKING:
    from ..models import Assignment, User


class UserMessageConfig(DispatcherConfig):
    auto_assign = forms.BooleanField(
        label=_("auto_assign"), required=False, help_text=_("Automatically assign users to this channel")
    )
    event = forms.ModelChoiceField(
        queryset=None,
        label=_("event"),
        widget=UnfoldAdminSelect2Widget,
        help_text=_("Event to trigger to notify user the presence of new messages"),
    )
    message_ttl = forms.IntegerField(help_text=_("Number of days read messages will be kept before automatic deletion"))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        from bitcaster.models import Event

        super().__init__(*args, **kwargs)
        self.fields["event"].queryset = Event.objects.all()

    def clean_event(self) -> int:
        event = self.cleaned_data["event"]
        channels = list(event.channels.all())
        match len(channels):
            case 0:
                raise ValidationError(_("Event does not have any Channel configured"))
            case 1:
                ch = channels[0]
                if str(ch.pk) != str(config.SYSTEM_EMAIL_CHANNEL):
                    raise ValidationError(_("Event must use system Email Channel"))
            case _:
                raise ValidationError(_("Event must have only one Channel configured"))

        if not event.notifications.filter(external_filtering=True).exists():
            raise ValidationError(_("At least one notification with external_filtering=True must be configured"))
        if not event.messages.exists():
            raise ValidationError(_("Event does not have any Message Template configured"))

        return event.pk


class UserMessageDispatcher(Dispatcher):
    slug = "system-email"
    verbose_name = "User Messages"
    backend = None
    protocol: MessageProtocol = MessageProtocol.INTERNAL
    config_class: type[DispatcherConfig] = UserMessageConfig
    default_config = {"message_ttl": 7, "auto_assign": True}

    def get_extra_config_info(self) -> str:
        from bitcaster.models import Event

        if event_pk := self.channel.config.get("event"):
            event = Event.objects.filter(pk=event_pk).first()
            return render_string(
                """
    <div class="grid grid-cols-2 gap-4">
    <div>Event</div><div><a href="{% url 'admin:bitcaster_event_change' event.pk %}">{{event}}</div>
    <div>Channel</div>
    <div><a href="{% url 'admin:bitcaster_channel_change' event.channels.first.pk %}">{{event.channels.first}}</a></div>
    <div>Message</div>
    <div>
    <a href="{% url 'admin:bitcaster_messagetemplate_change' event.messages.first.pk %}">{{event.messages.first}}</div>
    </div>
    """,
                {"event": event},
            )
        return ""

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        subject: str = f"{self.channel.subject_prefix}{payload.subject or ''}"
        user: "User" = assignment.address.user
        event = payload.event if payload.event.pk else None
        user.bitcaster_messages.create(
            subject=subject,
            message=payload.html_message or payload.message,
            event=event,
            level=payload.level or logging.INFO,
        )
        return True
