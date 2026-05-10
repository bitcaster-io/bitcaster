from typing import TYPE_CHECKING, Any

import logging

from anymail.backends.sendgrid import EmailBackend as SendgridBackend

from django import forms
from django.core.mail import EmailMultiAlternatives
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from .base import DispatcherConfig, Payload
from .email import BaseEmailDispatcher
from ..exceptions import DispatcherError

if TYPE_CHECKING:
    from bitcaster.models import Assignment
    from bitcaster.types.dispatcher import DispatcherHandler

logger = logging.getLogger(__name__)


class SendgridConfig(DispatcherConfig):
    api_key = forms.CharField(label=_("API Key"), widget=forms.PasswordInput)
    from_address = forms.EmailField(label=_("From Address"), required=False)
    from_label = forms.CharField(label=_("From Name"), required=False)

    help_text = "Create an API Key in your SendGrid account: Settings > API Keys > Create API Key > Full Access."


class SendGridDispatcher(BaseEmailDispatcher):
    slug = "sendgrid"
    verbose_name = "Sendgrid Email"
    config_class = SendgridConfig
    backend = SendgridBackend

    def get_connection(self) -> "DispatcherHandler":
        backend_kwargs = {"api_key": self.config["api_key"]}
        if isinstance(self.backend, str):
            klass = import_string(self.backend)
        else:
            klass = self.backend
        return klass(fail_silently=False, **backend_kwargs)

    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        try:
            subject = f"{self.channel.subject_prefix}{payload.subject or ''}"
            from_email = self.config.get("from_address") or self.channel.from_email
            from_label = self.config.get("from_label") or ""
            if from_label:
                from_email = f"{from_label} <{from_email}>"

            email = EmailMultiAlternatives(
                subject=subject or "",
                body=payload.message,
                from_email=from_email,
                to=[address],
                connection=self.get_connection(),
            )
            if payload.html_message:
                email.attach_alternative(payload.html_message, "text/html")
            email.send()
            return True
        except Exception as e:
            logger.exception(e)
            raise DispatcherError(str(e)) from e
