from anymail.backends.resend import EmailBackend as ResendBackend

from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.dispatchers.base import DispatcherConfig

from .base import AnyMailDispatcher


class ResendConfig(DispatcherConfig):
    api_key = forms.CharField(label=_("API Key"), widget=forms.PasswordInput)

    help_text = "Create an API Key in your Resend account: https://resend.com/api-keys"


class ResendDispatcher(AnyMailDispatcher):
    slug = "resend"
    verbose_name = "Resend Email"
    config_class = ResendConfig
    backend = ResendBackend
