import logging
from typing import Type

from django import forms
from django.utils.translation import gettext as _
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client
from twilio.rest.api.v2010.account.message import MessageInstance

from ..exceptions import DispatcherError
from .base import Dispatcher, DispatcherConfig, Payload

logger = logging.getLogger(__name__)


class TwilioConfig(DispatcherConfig):
    sid = forms.CharField(label=_("SID"))
    token = forms.CharField(label=_("Token"))
    number = forms.CharField(label=_("Number"))


class TwilioSMS(Dispatcher):
    id = 500
    slug = "sms"
    verbose_name = "SMS (Twilio)"
    config_class: Type[DispatcherConfig] = TwilioConfig

    def send(self, address: str, payload: Payload) -> MessageInstance:
        try:
            number = self.config.pop("number")
            client = Client(username=self.config["sid"], password=self.config["token"])
            return client.messages.create(
                body=payload.message,
                from_=number,
                to=address,
            )
        except TwilioRestException as e:
            logger.exception(e)
            raise DispatcherError(e)
