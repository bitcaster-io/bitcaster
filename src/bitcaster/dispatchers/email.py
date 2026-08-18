from typing import TYPE_CHECKING, Any

import logging

from django import forms
from django.core.mail import EmailMultiAlternatives
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import PasswordInput
from django.utils.translation import gettext_lazy as _

from .base import Dispatcher, DispatcherConfig, MessageProtocol, Payload
from ..exceptions import DispatcherError

if TYPE_CHECKING:
    from bitcaster.models import Assignment


logger = logging.getLogger(__name__)


class BaseEmailDispatcher(Dispatcher):
    abstract = True
    protocol: MessageProtocol = MessageProtocol.EMAIL

    def get_from_email(self) -> str:
        return self.channel.from_email

    def _send(self, address: str, payload: Payload, assignment: "Assignment | None" = None, **kwargs: Any) -> bool:
        try:
            subject: str = f"{self.channel.subject_prefix}{payload.subject or ''}"
            email = EmailMultiAlternatives(
                subject=subject or "",
                body=payload.message,
                from_email=self.get_from_email(),
                to=[address],
                connection=self.get_connection(),
            )
            if payload.html_message:
                email.attach_alternative(payload.html_message, "text/html")
            email.send()
            return True
        except Exception as e:
            logger.exception(e)
            if "is an invalid email address" in str(e):
                raise DispatcherError(
                    "The 'From Email' is not a valid email address. "
                    "Please check your Channel's 'From Email' configuration."
                ) from e
            raise DispatcherError(e) from e


class EmailConfig(DispatcherConfig):
    host = forms.CharField(label=_("Host"))
    port = forms.CharField(label=_("Port"))
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=PasswordInput)
    use_tls = forms.BooleanField(label=_("TLS"), required=False)
    use_ssl = forms.BooleanField(label=_("SSL"), required=False)
    timeout = forms.IntegerField(
        label=_("Timeout"),
        initial=3,
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )


class EmailDispatcher(BaseEmailDispatcher):
    slug = "email"
    verbose_name = "Email"
    config_class: type[DispatcherConfig] = EmailConfig
    backend = "django.core.mail.backends.smtp.EmailBackend"
