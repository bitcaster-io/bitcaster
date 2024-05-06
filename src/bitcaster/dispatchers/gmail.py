from typing import TYPE_CHECKING, Any, Dict

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .base import Dispatcher, DispatcherConfig, Payload

if TYPE_CHECKING:
    from bitcaster.types.dispatcher import TDispatcherConfig


class GMailConfig(DispatcherConfig):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"))


class GMailDispatcher(Dispatcher):
    slug = "gmail"
    verbose_name = "GMmail"

    config_class = GMailConfig
    backend = EmailBackend

    @cached_property
    def config(self) -> Dict[str, Any]:
        cfg: "TDispatcherConfig" = self.config_class(data=self.channel.config)
        if not cfg.is_valid():
            raise ValidationError(cfg.errors)
        config = {
            "host": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            **cfg.cleaned_data,
        }
        return config

    def send(self, address: str, payload: Payload) -> None:
        subject: str = f"{self.channel.subject_prefix}{payload.subject or ''}"
        email = EmailMultiAlternatives(
            subject=subject,
            body=payload.message,
            from_email=self.channel.from_email,
            to=[address],
            connection=self.get_connection(),
        )
        if payload.html_message:
            email.attach_alternative(payload.html_message, "text/html")
        email.send()
