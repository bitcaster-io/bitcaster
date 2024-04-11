from django import forms
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import gettext_lazy as _

from .base import Dispatcher, DispatcherConfig, Payload


class EmailConfig(DispatcherConfig):
    API_KEY = forms.CharField(label=_("API Key"))
    API_SECRET = forms.CharField(label=_("API Secret"))


class SystemEmailDispatcher(Dispatcher):
    id = 3
    slug = "email"
    local = True
    verbose_name = "System Email"
    text_message = True
    html_message = True
    config_class = EmailConfig
    backend = "django.core.mail.backends.smtp.EmailBackend"

    def send(self, address: str, payload: Payload) -> None:
        email = EmailMultiAlternatives(
            subject=payload.subject or "",
            body=payload.message,
            from_email=self.config["from_email"],
            to=[address],
            connection=self.get_connection(),
        )
        if payload.html_message:
            email.attach_alternative(payload.html_message, "text/html")
        email.send()
