from django import forms
from django.utils.translation import gettext_lazy as _

from ..base import DispatcherConfig


class AnymailConfig(DispatcherConfig):
    api_key = forms.CharField(label=_("API Key"), widget=forms.PasswordInput)
    from_address = forms.EmailField(label=_("From Address"), required=False)
    from_label = forms.CharField(label=_("From Name"), required=False)
