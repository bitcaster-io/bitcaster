from anymail.backends.mailjet import EmailBackend as MailjetBackend
from django import forms
from django.utils.translation import gettext_lazy as _

from .base import DispatcherConfig
from .email import EmailDispatcher


class MailJetConfig(DispatcherConfig):
    api_key = forms.CharField(label=_("API Key"))
    secret_key = forms.CharField(label=_("API Secret"))


class MailJetDispatcher(EmailDispatcher):
    slug = "mailjet"
    verbose_name = "Mailjet Email"
    config_class = MailJetConfig
    backend = MailjetBackend
