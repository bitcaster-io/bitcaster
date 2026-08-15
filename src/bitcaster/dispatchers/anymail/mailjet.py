from typing import TYPE_CHECKING, Any

import logging

from anymail.backends.mailjet import EmailBackend as MailjetBackend
from mailjet_rest import Client

from django import forms
from django.utils.translation import gettext_lazy as _

from .config import AnymailConfig
from ..base import Payload
from ..email import BaseEmailDispatcher
from ...exceptions import DispatcherError

if TYPE_CHECKING:
    from requests import Response

    from bitcaster.models import Assignment

logger = logging.getLogger(__name__)


class MailJetConfig(AnymailConfig):
    from_address = forms.EmailField(label=_("From Address"))
    secret_key = forms.CharField(label=_("API Secret"), widget=forms.PasswordInput)


class MailJetDispatcher(BaseEmailDispatcher):
    slug = "mailjet"
    verbose_name = "Mailjet Email"
    config_class = MailJetConfig
    backend = MailjetBackend

    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        mailjet: Client = Client(auth=(self.config["api_key"], self.config["secret_key"]), version="v3.1")
        data = {
            "Messages": [
                {
                    "From": {
                        "Email": self.config["from_address"],
                        "Name": self.config["from_label"],
                    },
                    "To": [{"Email": address, "Name": ""}],
                    "Subject": payload.subject,
                    "TextPart": payload.message,
                    "HTMLPart": payload.html_message,
                }
            ]
        }
        result: Response = mailjet.send.create(data=data)
        if result.status_code != 200:
            logger.error(result.text)
            raise DispatcherError("Generic Error")
        return True
