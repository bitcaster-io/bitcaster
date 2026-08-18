from anymail.backends.brevo import EmailBackend as BrevoBackend

from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.dispatchers.base import DispatcherConfig

from .base import AnyMailDispatcher


class BrevoConfig(DispatcherConfig):
    api_key = forms.CharField(label=_("API Key"), widget=forms.PasswordInput)

    help_text = "Create an API Key in your Brevo account: https://app.brevo.com/settings/keys/api"


class BrevoDispatcher(AnyMailDispatcher):
    slug = "brevo"
    verbose_name = "Brevo Email"
    config_class = BrevoConfig
    backend = BrevoBackend
