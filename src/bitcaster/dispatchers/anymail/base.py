from django import forms
from django.utils.translation import gettext_lazy as _

from bitcaster.dispatchers.base import DispatcherConfig
from bitcaster.dispatchers.email import BaseEmailDispatcher


class AnyMailConfig(DispatcherConfig):
    api_key = forms.CharField(label=_("API Key"))
    sender_domain = forms.CharField(label=_("Sender Domain"))


class AnyMailDispatcher(BaseEmailDispatcher):
    abstract = True
    verbose_name = "Email"
    config_class: type[DispatcherConfig] = AnyMailConfig
    backend = None
