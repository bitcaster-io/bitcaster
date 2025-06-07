from typing import TYPE_CHECKING, Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .base import Dispatcher, DispatcherConfig, MessageProtocol, Payload

if TYPE_CHECKING:
    from bitcaster.types.dispatcher import TDispatcherConfig

    from ..models import Assignment


class GMailConfig(DispatcherConfig):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)
    timeout = forms.IntegerField(
        label=_("Timeout"),
        initial=3,
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )


class GMailDispatcher(Dispatcher):
    slug = "gmail"
    verbose_name = "GMmail"

    config_class = GMailConfig
    backend: type[EmailBackend] = EmailBackend
    protocol: MessageProtocol = MessageProtocol.EMAIL

    @cached_property
    def config(self) -> dict[str, Any]:
        cfg: "TDispatcherConfig" = self.config_class(data=self.channel.config)
        if not cfg.is_valid():
            raise ValidationError(cfg.errors)
        return {
            "host": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            **cfg.cleaned_data,
        }

    def send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
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
        return email.send() > 0
