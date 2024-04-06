from django import forms
from django.utils.translation import gettext_lazy as _
from mailjet_rest import Client

from bitcaster.dispatchers.base import Config, Dispatcher, Payload


class MailJetConfig(Config):
    API_KEY = forms.CharField(label=_("API Key"))
    API_SECRET = forms.CharField(label=_("API Secret"))


class MailJetEmail(Dispatcher):
    id = 2
    slug = "mailjet-email"
    local = True
    verbose_name = "MailJet Email"
    text_message = True
    html_message = True
    config_class = MailJetConfig

    @classmethod
    def send_message(self, address: str, payload: Payload) -> None:
        mailjet = Client(auth=(self.config["API_KEY"], self.config["API_SECRET"]))
        data = {
            "Messages": [
                {
                    "From": {"Email": self.config["sender"], "Name": "Me"},
                    "To": [
                        {
                            "Email": address,
                            # "Name": "You"
                        }
                    ],
                    "Subject": payload.subject,
                    "TextPart": payload.message,
                    "HTMLPart": payload.html_message,
                }
            ]
        }
        result = mailjet.send.create(data=data)
        return result
