import logging
from typing import TYPE_CHECKING, Any

from django import forms
from django.utils.translation import gettext as _
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from ..exceptions import DispatcherError
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

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        try:
            number = self.config.pop("number")
            client = Client(username=self.config["sid"], password=self.config["token"])
            client.messages.create(
                body=payload.message,
                from_=number,
                to=address,
            )

            return True
        except TwilioRestException as e:
            logger.exception(e)
            raise DispatcherError(e) from e
