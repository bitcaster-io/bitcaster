from anymail.backends.mailgun import EmailBackend as MailgunBackend

from .base import AnyMailConfig, AnyMailDispatcher


class MailgunDispatcher(AnyMailDispatcher):
    slug = "mailgun"
    verbose_name = "Mailgun Email"
    config_class = AnyMailConfig
    backend = MailgunBackend
