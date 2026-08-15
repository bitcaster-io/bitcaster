from django import forms
from django.core.mail.backends.smtp import EmailBackend
from django.utils.translation import gettext_lazy as _

from .email import BaseEmailDispatcher, SMTPConfig


class GMailConfig(SMTPConfig):
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, required=False)


class GMailDispatcher(BaseEmailDispatcher):
    slug = "gmail"
    verbose_name = "GMmail"

    config_class = GMailConfig
    backend: type[EmailBackend] = EmailBackend
    default_config = {"host": "smtp.gmail.com", "port": 587, "use_tls": True}
