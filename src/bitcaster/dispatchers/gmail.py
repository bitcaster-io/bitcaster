from typing import TYPE_CHECKING, Any

from django import forms
from django.core.exceptions import ValidationError
from django.core.mail.backends.smtp import EmailBackend
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _

from .base import DispatcherConfig
from .email import BaseEmailDispatcher

if TYPE_CHECKING:
    from bitcaster.types.dispatcher import TDispatcherConfig_co


class GMailConfig(DispatcherConfig):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)
    timeout = forms.IntegerField(
        label=_("Timeout"),
        initial=3,
        required=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )


class GMailDispatcher(BaseEmailDispatcher):
    slug = "gmail"
    verbose_name = "Gmail"

    config_class = GMailConfig
    backend: type[EmailBackend] = EmailBackend

    @property
    def config(self) -> dict[str, Any]:
        cfg: "TDispatcherConfig_co" = self.config_class(data=self.channel.config)
        if not cfg.is_valid():
            raise ValidationError(cfg.errors)
        return {
            "host": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            **cfg.cleaned_data,
        }
