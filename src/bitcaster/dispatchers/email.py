import logging
from typing import Type

from django import forms
from django.core.mail import EmailMultiAlternatives
from django.forms import PasswordInput
from django.utils.translation import gettext_lazy as _

from ..exceptions import DispatcherError
from .base import Dispatcher, DispatcherConfig, Payload, Protocol

logger = logging.getLogger(__name__)


class EmailConfig(DispatcherConfig):
    host = forms.CharField(label=_("Host"))
    port = forms.CharField(label=_("Port"))
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=PasswordInput)
    use_tls = forms.BooleanField(label=_("TLS"), required=False)
    use_ssl = forms.BooleanField(label=_("SSL"), required=False)
    timeout = forms.IntegerField(label=_("Timeout"), required=False)


class EmailDispatcher(Dispatcher):
    slug = "email"
    verbose_name = "Email"
    protocol: Protocol = Protocol.EMAIL

    config_class: Type[DispatcherConfig] = EmailConfig
    backend = "django.core.mail.backends.smtp.EmailBackend"

    def send(self, address: str, payload: Payload) -> None:
        try:
            subject: str = f"{self.channel.subject_prefix}{payload.subject or ''}"
            email = EmailMultiAlternatives(
                subject=subject or "",
                body=payload.message,
                from_email=self.channel.from_email,
                to=[address],
                connection=self.get_connection(),
            )
            if payload.html_message:
                email.attach_alternative(payload.html_message, "text/html")
            email.send()
        except Exception as e:
            logger.exception(e)
            raise DispatcherError(e)
