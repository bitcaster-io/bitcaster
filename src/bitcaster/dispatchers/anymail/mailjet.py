from anymail.backends.mailjet import EmailBackend as MailjetBackend

from django import forms
from django.utils.translation import gettext_lazy as _

from .base import AnyMailDispatcher
from ..base import DispatcherConfig


class MailJetConfig(DispatcherConfig):
    api_key = forms.CharField(label=_("API Key"), widget=forms.PasswordInput)
    secret_key = forms.CharField(label=_("API Secret"), widget=forms.PasswordInput)
    from_address = forms.EmailField(label=_("From Address"), required=False)
    from_label = forms.CharField(label=_("From Name"), required=False)


class MailJetDispatcher(AnyMailDispatcher):
    slug = "mailjet"
    verbose_name = "Mailjet Email"
    config_class = MailJetConfig
    backend = MailjetBackend

    def get_from_email(self) -> str:
        from_email = self.config.get("from_address") or self.channel.from_email
        from_label = self.config.get("from_label") or ""
        if from_label:
            from_email = f"{from_label} <{from_email}>"
        return from_email
