import logging
from typing import Type

from django import forms
from django.utils.translation import gettext as _
from twilio.rest import Client

from .base import Dispatcher, DispatcherConfig, Payload

logger = logging.getLogger(__name__)


class TwilioConfig(DispatcherConfig):
    sid = forms.CharField(label=_("SID"))
    token = forms.CharField(label=_("Token"))
    number = forms.CharField(label=_("Number"))


class TwilioSMS(Dispatcher):
    id = 500
    slug = "sms"
    config_class: Type[DispatcherConfig] = TwilioConfig

    def send(self, address: str, payload: Payload) -> None:
        number = self.config.pop("number")
        client = Client(**self.config)
        client.messages.create(
            body=payload.message,
            from_=number,
            to=address,
        )
