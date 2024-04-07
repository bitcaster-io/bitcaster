from django import forms
from django.utils.translation import gettext_lazy as _

from .base import Config, Dispatcher


class EmailConfig(Config):
    API_KEY = forms.CharField(label=_("API Key"))
    API_SECRET = forms.CharField(label=_("API Secret"))


class EmailDispatcher(Dispatcher):
    id = 2
    slug = "email"
    local = True
    verbose_name = "Email"
    text_message = True
    html_message = True
    config_class = EmailConfig