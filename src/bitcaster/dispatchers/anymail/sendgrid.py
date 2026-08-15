from typing import Any

from anymail.backends.sendgrid import EmailBackend as SendgridBackend

from .config import AnymailConfig
from ..base import Payload
from ..email import BaseEmailDispatcher


class SendgridConfig(AnymailConfig):
    help_text = "Create an API Key in your SendGrid account: Settings > API Keys > Create API Key > Full Access."


class SendGridDispatcher(BaseEmailDispatcher):
    slug = "sendgrid"
    verbose_name = "Sendgrid Email"
    config_class = SendgridConfig
    backend = SendgridBackend

    def get_backend_kwargs(self) -> dict[str, Any]:
        return {"api_key": self.config["api_key"]}

    def get_from_email(self, payload: Payload) -> str:
        from_email = self.config.get("from_address") or self.channel.from_email
        if from_label := self.config.get("from_label"):
            return f"{from_label} <{from_email}>"
        return from_email
