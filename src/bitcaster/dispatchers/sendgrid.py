from anymail.backends.sendgrid import EmailBackend as SendgridBackend
from django import forms
from django.utils.translation import gettext_lazy as _

from .base import DispatcherConfig
from .email import EmailDispatcher


class SendgridConfig(DispatcherConfig):
    api_key = forms.CharField(label=_("API Key"))


class SendGridDispatcher(EmailDispatcher):
    slug = "sendgrid"
    verbose_name = "Sendgrid Email"
    config_class = SendgridConfig
    backend = SendgridBackend
