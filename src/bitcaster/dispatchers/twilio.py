import logging
from typing import TYPE_CHECKING, Any

from django import forms
from django.utils.translation import gettext_lazy as _
from twilio.rest import Client

from .base import Dispatcher, DispatcherConfig, MessageProtocol, Payload

if TYPE_CHECKING:
    from ..models import Assignment

logger = logging.getLogger(__name__)


class TwilioConfig(DispatcherConfig):
    sid = forms.CharField(label=_("SID"))
    token = forms.CharField(label=_("Token"))
    number = forms.CharField(label=_("Number"))


class TwilioSMS(Dispatcher):
    id = 500
    slug = "sms"
    verbose_name = "SMS (Twilio)"
    config_class: type[DispatcherConfig] = TwilioConfig
    protocol = MessageProtocol.SMS

    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        number = self.config.pop("number")
        client = Client(username=self.config["sid"], password=self.config["token"])
        client.messages.create(
            body=payload.message,
            from_=number,
            to=address,
        )
        return True
