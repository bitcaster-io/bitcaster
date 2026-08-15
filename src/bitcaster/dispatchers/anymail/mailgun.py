from anymail.backends.mailgun import EmailBackend as MailgunBackend

from django import forms
from django.utils.translation import gettext_lazy as _

from .config import AnymailConfig
from ..email import EmailDispatcher


class MailgunConfig(AnymailConfig):
    api_key = forms.CharField(label=_("API Key"))
    sender_domain = forms.CharField(label=_("Sender Domain"))


class MailgunDispatcher(EmailDispatcher):
    slug = "maiilgun"
    verbose_name = "Mailgun Email"
    config_class = MailgunConfig
    backend = MailgunBackend
