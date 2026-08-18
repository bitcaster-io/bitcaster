from typing import TYPE_CHECKING

from anymail.backends.sendgrid import EmailBackend as SendgridBackend

from django import forms
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from .base import AnyMailConfig, AnyMailDispatcher

if TYPE_CHECKING:
    from bitcaster.types.dispatcher import DispatcherHandler


class SendgridConfig(AnyMailConfig):
    sender_domain = forms.CharField(label=_("Sender Domain"), required=False)
    from_address = forms.EmailField(label=_("From Address"), required=False)
    from_label = forms.CharField(label=_("From Name"), required=False)

    help_text = "Create an API Key in your SendGrid account: Settings > API Keys > Create API Key > Full Access."


class SendGridDispatcher(AnyMailDispatcher):
    slug = "sendgrid"
    verbose_name = "Sendgrid Email"
    config_class = SendgridConfig
    backend = SendgridBackend

    def get_connection(self) -> "DispatcherHandler":
        backend_kwargs = {"api_key": self.config["api_key"]}
        if isinstance(self.backend, str):
            klass = import_string(self.backend)
        else:
            klass = self.backend
        return klass(fail_silently=False, **backend_kwargs)

    def get_from_email(self) -> str:
        from_email = self.config.get("from_address") or self.channel.from_email
        from_label = self.config.get("from_label") or ""
        if from_label:
            from_email = f"{from_label} <{from_email}>"
        return from_email
