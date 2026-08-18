from anymail.backends.postmark import EmailBackend as PostmarkBackend

from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.dispatchers.base import DispatcherConfig

from .base import AnyMailDispatcher


class PostmarkConfig(DispatcherConfig):
    server_token = forms.CharField(label=_("Server Token"), widget=forms.PasswordInput)

    help_text = "Create a Server Token in your Postmark account: https://account.postmarkapp.com/servers"


class PostmarkDispatcher(AnyMailDispatcher):
    slug = "postmark"
    verbose_name = "Postmark Email"
    config_class = PostmarkConfig
    backend = PostmarkBackend
